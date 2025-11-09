import json
import time
import random
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
import sys
import os
from pymongo import MongoClient

# Import config from backend module
from backend.config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample data for generating transactions - Indian Stocks (NSE)
SYMBOLS = [
    'RELIANCE',  # Reliance Industries
    'TCS',       # Tata Consultancy Services
    'HDFCBANK',  # HDFC Bank
    'INFY',      # Infosys
    'ICICIBANK', # ICICI Bank
    'HINDUNILVR',# Hindustan Unilever
    'BHARTIARTL',# Bharti Airtel
    'ITC',       # ITC Limited
    'SBIN',      # State Bank of India
    'LT',        # Larsen & Toubro
    'BAJFINANCE',# Bajaj Finance
    'ASIANPAINT',# Asian Paints
    'MARUTI',    # Maruti Suzuki
    'TITAN',     # Titan Company
    'WIPRO'      # Wipro
]

# Typical price ranges for Indian stocks (in INR)
PRICE_RANGES = {
    'RELIANCE': (2400, 2800),
    'TCS': (3500, 4000),
    'HDFCBANK': (1500, 1700),
    'INFY': (1400, 1600),
    'ICICIBANK': (900, 1100),
    'HINDUNILVR': (2300, 2600),
    'BHARTIARTL': (800, 1000),
    'ITC': (400, 450),
    'SBIN': (550, 650),
    'LT': (3200, 3600),
    'BAJFINANCE': (6500, 7500),
    'ASIANPAINT': (2800, 3200),
    'MARUTI': (10000, 12000),
    'TITAN': (3000, 3400),
    'WIPRO': (400, 500)
}

TRADER_IDS = [f'T{i:04d}' for i in range(1, 51)]  # 50 traders
ORDER_TYPES = ['buy', 'sell']

class TransactionProducer:
    def __init__(self):
        self.producer = None
        self.counter_file = '/tmp/transaction_counter.txt'
        self.transaction_counter = self._load_counter()
        logger.info(f"Starting from transaction counter: {self.transaction_counter}")

    def _load_counter(self):
        """Load the last transaction counter from MongoDB"""
        try:
            # Connect to MongoDB and get the highest transaction ID
            client = MongoClient(config.MONGO_URI)
            db = client[config.MONGO_DB]
            collection = db['trade_classifications']

            # Find the document with the highest trade_id
            result = collection.find_one(
                sort=[('trade_id', -1)],  # Sort descending
                projection={'trade_id': 1}
            )

            if result and 'trade_id' in result:
                # Extract number from trade_id (e.g., "TX00000123" -> 123)
                trade_id = result['trade_id']
                counter = int(trade_id.replace('TX', ''))
                logger.info(f"Loaded counter from MongoDB: {counter} (last ID: {trade_id})")
                client.close()
                return counter

            client.close()
            logger.info("No existing transactions found in MongoDB, starting from 0")
        except Exception as e:
            logger.warning(f"Could not load counter from MongoDB: {e}")

        return 0

    def _save_counter(self):
        """Save the current transaction counter to file"""
        try:
            with open(self.counter_file, 'w') as f:
                f.write(str(self.transaction_counter))
        except Exception as e:
            logger.error(f"Failed to save counter: {e}")

    def connect(self):
        """Connect to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8')
            )
            logger.info(f"Connected to Kafka at {config.KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def generate_transaction(self) -> dict:
        """Generate random transaction with ~25% being fraudulent patterns"""
        self.transaction_counter += 1
        trade_id = f"TX{self.transaction_counter:08d}"

        # Select random Indian stock
        symbol = random.choice(SYMBOLS)
        price_range = PRICE_RANGES[symbol]

        # Generate transaction with intentional fraud patterns in ~25% of cases
        fraud_type = random.random()

        if fraud_type < 0.75:  # 75% - Normal/Legitimate transactions
            # Normal institutional trade ranges
            quantity = random.randint(100, 75000)
            price_variation = random.uniform(0.6, 2.5)  # 60% to 250% of normal
            base_price = random.uniform(price_range[0], price_range[1])
            price = base_price * price_variation

        elif fraud_type < 0.85:  # 10% - Pump scheme (extreme high price)
            quantity = random.randint(5000, 95000)
            price_variation = random.uniform(4.5, 8.0)  # 450% to 800% of normal (extreme)
            base_price = random.uniform(price_range[0], price_range[1])
            price = base_price * price_variation

        elif fraud_type < 0.95:  # 10% - Wash trading (very low price + high quantity)
            quantity = random.randint(75000, 99000)  # Very high quantity
            price_variation = random.uniform(0.15, 0.35)  # 15% to 35% of normal (very low)
            base_price = random.uniform(price_range[0], price_range[1])
            price = base_price * price_variation

        else:  # 5% - Market manipulation (extreme quantity + extreme price)
            quantity = random.randint(85000, 99000)  # Very high quantity
            price_variation = random.uniform(4.0, 7.0)  # 400% to 700% of normal
            base_price = random.uniform(price_range[0], price_range[1])
            price = base_price * price_variation

        # Random trader from all available traders
        trader_id = random.choice(TRADER_IDS)

        # Use current local time
        from datetime import datetime
        current_time = datetime.now()

        transaction = {
            "trade_id": trade_id,
            "trader_id": trader_id,
            "symbol": symbol,
            "quantity": quantity,
            "price": round(price, 2),  # Price in INR
            "timestamp": current_time.isoformat(),
            "order_type": random.choice(ORDER_TYPES)
        }

        return transaction
    
    def send_transaction(self, transaction: dict):
        """Send transaction to Kafka"""
        try:
            trade_id = transaction['trade_id']
            future = self.producer.send(
                config.KAFKA_TOPIC,
                key=trade_id,
                value=transaction
            )

            # Wait for send to complete (blocking)
            record_metadata = future.get(timeout=10)

            logger.info(
                f"Sent {trade_id} - {transaction['symbol']} "
                f"Qty: {transaction['quantity']:,} Price: ₹{transaction['price']:.2f}"
            )

            # Save counter after successful send
            self._save_counter()

        except KafkaError as e:
            logger.error(f"Failed to send transaction: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending transaction: {e}")
    
    def start(self, interval: float = 2.0):
        """Start producing transactions at specified interval"""
        logger.info(f"Starting transaction producer (1 transaction every {interval}s)")
        
        try:
            while True:
                transaction = self.generate_transaction()
                self.send_transaction(transaction)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Producer interrupted by user")
        except Exception as e:
            logger.error(f"Producer error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop producer and close connection"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Producer stopped")

def main():
    """Main entry point"""
    producer = TransactionProducer()

    try:
        producer.connect()
        producer.start(interval=6.0)  # 10 transactions per minute
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
