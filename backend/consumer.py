import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

from config import config
from db import mongodb
from llm_chain import classifier
from schemas import Transaction, ClassificationDocument, LlamaResult

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SparkFraudDetectionConsumer:
    def __init__(self, socketio=None):
        self.spark: Optional[SparkSession] = None
        self.socketio = socketio
        self.running = False
        self.processed_trade_ids = set()  # For deduplication

    def create_spark_session(self):
        """Initialize Spark session with Kafka support"""
        try:
            self.spark = SparkSession.builder \
                .appName(config.SPARK_APP_NAME) \
                .master(config.SPARK_MASTER) \
                .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
                .config("spark.sql.streaming.checkpointLocation", config.SPARK_CHECKPOINT_DIR) \
                .getOrCreate()

            # Set log level to reduce verbosity
            self.spark.sparkContext.setLogLevel("WARN")

            logger.info(f"Spark session created: {config.SPARK_APP_NAME}")
        except Exception as e:
            logger.error(f"Failed to create Spark session: {e}")
            raise

    def start(self):
        """Start consuming messages from Kafka using Spark Structured Streaming"""
        self.running = True
        logger.info("Starting Spark fraud detection consumer...")

        try:
            # Define schema for transaction JSON
            transaction_schema = StructType([
                StructField("trade_id", StringType(), False),
                StructField("trader_id", StringType(), False),
                StructField("symbol", StringType(), False),
                StructField("quantity", IntegerType(), False),
                StructField("price", FloatType(), False),
                StructField("timestamp", StringType(), False),
                StructField("order_type", StringType(), False)
            ])

            # Read from Kafka
            df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", config.KAFKA_BOOTSTRAP_SERVERS) \
                .option("subscribe", config.KAFKA_TOPIC) \
                .option("startingOffsets", config.SPARK_KAFKA_OFFSET) \
                .option("failOnDataLoss", "false") \
                .load()

            # Parse the value column (JSON string) into structured data
            parsed_df = df.select(
                col("key").cast("string").alias("trade_id_key"),
                from_json(col("value").cast("string"), transaction_schema).alias("data")
            ).select("trade_id_key", "data.*")

            # Process each micro-batch
            query = parsed_df \
                .writeStream \
                .foreachBatch(self.process_batch) \
                .trigger(processingTime=config.SPARK_TRIGGER_INTERVAL) \
                .start()

            logger.info("Spark streaming query started")

            # Wait for termination
            query.awaitTermination()

        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
            raise
        finally:
            self.stop()

    def process_batch(self, batch_df: DataFrame, batch_id: int):
        """Process each micro-batch of transactions"""
        logger.info(f"Processing batch {batch_id} with {batch_df.count()} records")

        # Convert to list of rows for processing
        transactions = batch_df.collect()

        for row in transactions:
            try:
                trade_id = row.trade_id

                # Deduplicate
                if trade_id in self.processed_trade_ids:
                    logger.info(f"Skipping duplicate trade_id: {trade_id}")
                    continue

                # Build transaction data
                transaction_data = {
                    "trade_id": row.trade_id,
                    "trader_id": row.trader_id,
                    "symbol": row.symbol,
                    "quantity": row.quantity,
                    "price": row.price,
                    "timestamp": row.timestamp,
                    "order_type": row.order_type
                }

                start_time = time.time()

                # Process with retry logic
                success = self.process_transaction(transaction_data, start_time)

                if success:
                    self.processed_trade_ids.add(trade_id)

            except Exception as e:
                logger.error(f"Error processing transaction in batch {batch_id}: {e}")

    def process_transaction(self, transaction_data: dict, start_time: float) -> bool:
        """Process a single transaction with retry logic"""
        retry_count = 0
        max_retries = config.MAX_RETRIES

        while retry_count <= max_retries:
            try:
                # Validate transaction
                transaction = Transaction(**transaction_data)

                # Classify with LLM
                llama_result, llm_latency = classifier.classify(transaction)

                # Create classification document with timezone-aware timestamp
                processed_at = datetime.now(timezone.utc)
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

                # Emit via WebSocket
                if self.socketio:
                    self._emit_updates(doc_dict, stats)

                logger.info(f"Successfully processed {transaction.trade_id} - {llama_result.label} ({llama_result.confidence:.2f})")
                return True

            except Exception as e:
                retry_count += 1
                logger.error(f"Error processing {transaction_data.get('trade_id')} (attempt {retry_count}/{max_retries}): {e}")

                if retry_count > max_retries:
                    # Send to DLQ (you could implement Kafka write here if needed)
                    self._log_dlq(transaction_data, str(e))
                    return False
                else:
                    # Exponential backoff
                    backoff = config.RETRY_BACKOFF_BASE ** retry_count
                    logger.info(f"Retrying in {backoff}s...")
                    time.sleep(backoff)

        return False

    def _emit_updates(self, doc: dict, stats: dict):
        """Emit updates via WebSocket"""
        try:
            # Prepare transaction data
            transaction_data = {
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
            }

            # Combine both updates into a single event for atomic frontend update
            combined_update = {
                'stats': stats,
                'transaction': transaction_data
            }
            self.socketio.emit('transaction_update', combined_update)
            logger.info(f"✅ Emitted transaction_update: {doc['trade_id']} ({doc['llama_result']['label']}) | Stats: {stats}")

            # Also emit individual events for backward compatibility
            self.socketio.emit('summary_counts', stats)
            self.socketio.emit('transaction_stream', transaction_data)

        except Exception as e:
            logger.error(f"❌ Failed to emit WebSocket updates: {e}")

    def _log_dlq(self, message: dict, error: str):
        """Log failed message (DLQ replacement)"""
        try:
            dlq_message = {
                "original_message": message,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
            logger.error(f"DLQ: {json.dumps(dlq_message)}")
            # You could also write this to a file or separate MongoDB collection
        except Exception as e:
            logger.error(f"Failed to log DLQ message: {e}")

    def stop(self):
        """Stop consumer gracefully"""
        self.running = False
        if self.spark:
            self.spark.stop()
        logger.info("Spark consumer stopped")
