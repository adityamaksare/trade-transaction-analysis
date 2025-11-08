import os
from typing import Optional

class Config:
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC", "transactions")
    KAFKA_DLQ_TOPIC: str = os.getenv("KAFKA_DLQ_TOPIC", "transactions_dlq")
    KAFKA_GROUP_ID: str = os.getenv("KAFKA_GROUP_ID", "fraud-detector-group")

    # Spark Configuration
    SPARK_APP_NAME: str = os.getenv("SPARK_APP_NAME", "FraudDetectionStreaming")
    SPARK_MASTER: str = os.getenv("SPARK_MASTER", "local[*]")
    SPARK_CHECKPOINT_DIR: str = os.getenv("SPARK_CHECKPOINT_DIR", "./spark-checkpoint")
    SPARK_KAFKA_OFFSET: str = os.getenv("SPARK_KAFKA_OFFSET", "earliest")  # earliest or latest
    SPARK_TRIGGER_INTERVAL: str = os.getenv("SPARK_TRIGGER_INTERVAL", "1 second")
    
    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "fraud_detection")
    MONGO_COLLECTION_CLASSIFICATIONS: str = "trade_classifications"
    MONGO_COLLECTION_STATS: str = "stats"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    
    # Flask Configuration
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # WebSocket Configuration
    SOCKETIO_ASYNC_MODE: str = "threading"
    CORS_ALLOWED_ORIGINS: str = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    
    # Retry Configuration
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_BACKOFF_BASE: float = float(os.getenv("RETRY_BACKOFF_BASE", "2.0"))

config = Config()
