from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from config import config

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.classifications: Optional[Collection] = None
        self.stats: Optional[Collection] = None
        
    def connect(self):
        """Connect to MongoDB and set up collections with indexes"""
        try:
            self.client = MongoClient(config.MONGO_URI)
            self.db = self.client[config.MONGO_DB]
            self.classifications = self.db[config.MONGO_COLLECTION_CLASSIFICATIONS]
            self.stats = self.db[config.MONGO_COLLECTION_STATS]
            
            # Create indexes
            self.classifications.create_index([("trade_id", ASCENDING)], unique=True)
            self.classifications.create_index([("timestamp", DESCENDING)])
            self.classifications.create_index([("llama_result.label", ASCENDING), ("timestamp", DESCENDING)])
            
            # Initialize stats document if it doesn't exist
            self.stats.update_one(
                {"_id": "stats"},
                {
                    "$setOnInsert": {
                        "total": 0,
                        "legit": 0,
                        "fraud": 0,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            logger.info("MongoDB connected and indexes created")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
            
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
    
    def insert_classification(self, document: Dict[str, Any]) -> bool:
        """
        Insert or update a trade classification document
        Returns True on success, False on failure
        """
        try:
            # Upsert by trade_id for idempotency
            self.classifications.update_one(
                {"trade_id": document["trade_id"]},
                {"$set": document},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to insert classification: {e}")
            return False
    
    def update_stats(self, label: str) -> Dict[str, int]:
        """
        Atomically update stats counters
        Returns the updated stats
        """
        try:
            result = self.stats.find_one_and_update(
                {"_id": "stats"},
                {
                    "$inc": {
                        "total": 1,
                        label: 1
                    },
                    "$set": {
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
            
            return {
                "total": result["total"],
                "legit": result["legit"],
                "fraud": result["fraud"]
            }
        except Exception as e:
            logger.error(f"Failed to update stats: {e}")
            raise
    
    def get_stats(self) -> Dict[str, int]:
        """Get current stats"""
        try:
            result = self.stats.find_one({"_id": "stats"})
            if result:
                return {
                    "total": result["total"],
                    "legit": result["legit"],
                    "fraud": result["fraud"]
                }
            return {"total": 0, "legit": 0, "fraud": 0}
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"total": 0, "legit": 0, "fraud": 0}
    
    def get_transactions(self, limit: int = 100, label: Optional[str] = None, skip: int = 0) -> List[Dict[str, Any]]:
        """Get paginated transaction history"""
        try:
            query = {}
            if label:
                query["llama_result.label"] = label
                
            cursor = self.classifications.find(query).sort("timestamp", DESCENDING).skip(skip).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            return []

# Singleton instance
mongodb = MongoDB()
