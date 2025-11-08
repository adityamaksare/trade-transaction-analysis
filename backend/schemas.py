from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime

class Transaction(BaseModel):
    """Transaction input schema"""
    trade_id: str
    trader_id: str
    symbol: str
    quantity: int
    price: float
    timestamp: str
    order_type: Literal["buy", "sell"]
    
class LlamaResult(BaseModel):
    """LLM output schema with forced binary classification"""
    label: Literal["fraud", "legit"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1"""
        return max(0.0, min(1.0, v))

class ClassificationDocument(BaseModel):
    """Final document stored in MongoDB"""
    trade_id: str
    trader_id: str
    symbol: str
    quantity: int
    price: float
    timestamp: str
    order_type: str
    llama_result: LlamaResult
    processed_at: datetime
    consumer_metadata: dict
    raw_message: Optional[dict] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v.tzinfo else v.isoformat() + 'Z'
        }
