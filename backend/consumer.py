import json
import logging
import time
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from typing import Optional

from config import config
from db import mongodb
from llm_chain import classifier
from schemas import Transaction, ClassificationDocument

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FraudDetectionConsumer:
    def __init__(self, socketio=None):
        self.consumer: Optional[KafkaConsumer] = None
        self.dlq_producer: Optional[KafkaProducer] = None
        self.socketio = socketio
        self.running = False
        self.processed_trade_ids = set()  # For deduplication
        
    def connect(self):
        """Initialize Kafka consumer and DLQ producer"""
        try:
            self.consumer = KafkaConsumer(
                config.KAFKA_TOPIC,
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                group_id=config.KAFKA_GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                enable_auto_commit=False,  # Manual commit after success
                auto_offset_reset='earliest'
            )
            
            self.dlq_producer = KafkaProducer(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            
            logger.info(f"Connected to Kafka topic: {config.KAFKA_TOPIC}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def start(self):
        """Start consuming messages"""
        self.running = True
        logger.info("Starting fraud detection consumer...")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                self.process_message(message)
                
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop consumer gracefully"""
        self.running = False
        if self.consumer:
            self.consumer.close()
        if self.dlq_producer:
            self.dlq_producer.close()
        logger.info("Consumer stopped")
    
    def process_message(self, message):
        """Process a single Kafka message with retry logic"""
        trade_id = message.key
        
        # Deduplicate
        if trade_id in self.processed_trade_ids:
            logger.info(f"Skipping duplicate trade_id: {trade_id}")
            self.consumer.commit()
            return
        
        transaction_data = message.value
        start_time = time.time()
        
        retry_count = 0
        max_retries = config.MAX_RETRIES
        
        while retry_count <= max_retries:
            try:
                # Validate transaction
                transaction = Transaction(**transaction_data)
                
                # Classify with LLM
                llama_result, llm_latency = classifier.classify(transaction)
                
                # Create classification document
                processed_at = datetime.utcnow()
                end_to_end_latency = (time.time() - start_time) * 1000
                
                doc = ClassificationDocument(
                    trade_id=transaction.trade_id,
                    trader_id=transaction.trader_id,
                    symbol=transaction.symbol,
                    quantity=transaction.quantity,
                    price=transaction.price,
                    timestamp=transaction.timestamp,
                    order_type=transaction.order_type,
                    llama_result=llama_result,
                    processed_at=processed_at,
                    consumer_metadata={
                        "llm_latency_ms": llm_latency,
                        "end_to_end_latency_ms": end_to_end_latency,
                        "retry_count": retry_count
                    },
                    raw_message=transaction_data
                )
                
                # Write to MongoDB
                doc_dict = doc.model_dump(mode='json')
                success = mongodb.insert_classification(doc_dict)
                
                if not success:
                    raise Exception("Failed to insert into MongoDB")
                
                # Update stats
                stats = mongodb.update_stats(llama_result.label)
                
                # Mark as processed
                self.processed_trade_ids.add(trade_id)
                
                # Emit via WebSocket
                if self.socketio:
                    self._emit_updates(doc_dict, stats)
                
                # Commit offset
                self.consumer.commit()
                
                logger.info(f"Successfully processed {trade_id} - {llama_result.label} ({llama_result.confidence:.2f})")
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Error processing {trade_id} (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count > max_retries:
                    # Send to DLQ
                    self._send_to_dlq(transaction_data, str(e))
                    # Commit to move past this message
                    self.consumer.commit()
                    break
                else:
                    # Exponential backoff
                    backoff = config.RETRY_BACKOFF_BASE ** retry_count
                    logger.info(f"Retrying in {backoff}s...")
                    time.sleep(backoff)
    
    def _emit_updates(self, doc: dict, stats: dict):
        """Emit updates via WebSocket"""
        try:
            # Emit transaction stream
            self.socketio.emit('transaction_stream', {
                'trade_id': doc['trade_id'],
                'trader_id': doc['trader_id'],
                'symbol': doc['symbol'],
                'quantity': doc['quantity'],
                'price': doc['price'],
                'timestamp': doc['timestamp'],
                'order_type': doc['order_type'],
                'label': doc['llama_result']['label'],
                'confidence': doc['llama_result']['confidence'],
                'reason': doc['llama_result']['reason'],
                'processed_at': doc['processed_at'].isoformat() if isinstance(doc['processed_at'], datetime) else doc['processed_at']
            })
            
            # Emit summary counts
            self.socketio.emit('summary_counts', stats)
            
        except Exception as e:
            logger.error(f"Failed to emit WebSocket updates: {e}")
    
    def _send_to_dlq(self, message: dict, error: str):
        """Send failed message to Dead Letter Queue"""
        try:
            dlq_message = {
                "original_message": message,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.dlq_producer.send(config.KAFKA_DLQ_TOPIC, value=dlq_message)
            logger.info(f"Sent message to DLQ: {message.get('trade_id')}")
        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}")
