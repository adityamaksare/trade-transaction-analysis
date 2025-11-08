import json
import logging
import time
from typing import Dict, Any
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from config import config
from schemas import LlamaResult, Transaction

logger = logging.getLogger(__name__)

# Few-shot prompt template
PROMPT_TEMPLATE = """You are a fraud detection expert analyzing stock market transactions for Indian stocks.

Classify the following transaction as either "fraud" or "legit". You MUST choose one of these two labels - no "unknown" or other labels are allowed.

TYPICAL PRICE RANGES (in ₹):
RELIANCE: ₹2,400-2,800 | TCS: ₹3,500-4,000 | HDFCBANK: ₹1,500-1,700 | INFY: ₹1,400-1,600
ICICIBANK: ₹900-1,100 | HINDUNILVR: ₹2,300-2,600 | BHARTIARTL: ₹800-1,000 | ITC: ₹400-450
SBIN: ₹550-650 | LT: ₹3,200-3,600 | BAJFINANCE: ₹6,500-7,500 | ASIANPAINT: ₹2,800-3,200
MARUTI: ₹10,000-12,000 | TITAN: ₹3,000-3,400 | WIPRO: ₹400-500

FRAUD INDICATORS (flag as fraud if ANY of these):
1. **Pump Scheme**: Price >4x typical range (e.g., INFY at ₹6,400+, SBIN at ₹2,600+)
2. **Wash Trading**: Price <0.4x typical AND quantity >70,000 (e.g., BHARTIARTL <₹320 with 75k+ shares)
3. **Market Manipulation**: Quantity >85,000 AND price >3.5x OR <0.4x typical

LEGIT INDICATORS (default assumption):
- Normal institutional trades: 50,000-80,000 shares at 0.6x-2.5x typical price
- Large volume alone is NOT fraud: 70,000 shares at normal price is legitimate
- Price volatility alone is NOT fraud: 2.5x typical price with normal quantity is OK

EXAMPLES:
✅ LEGIT: RELIANCE 75,000 @ ₹2,650 (within normal range)
✅ LEGIT: INFY 60,000 @ ₹2,400 (1.6x typical, but quantity OK)
❌ FRAUD: INFY 20,000 @ ₹7,000 (4.6x typical = pump scheme)
❌ FRAUD: BHARTIARTL 91,000 @ ₹290 (0.32x typical + high qty = wash trading)
❌ FRAUD: SBIN 90,000 @ ₹2,800 (>85k qty + 4.7x typical = manipulation)

Transaction details:
Trade ID: {trade_id}
Trader ID: {trader_id}
Symbol: {symbol}
Quantity: {quantity}
Price: ₹{price}
Timestamp: {timestamp}
Order Type: {order_type}

Respond with ONLY a JSON object in this exact format (no additional text):
{{
  "label": "fraud" or "legit",
  "confidence": 0.0 to 1.0,
  "reason": "brief explanation"
}}"""

class FraudClassifier:
    def __init__(self):
        self.llm = Ollama(
            base_url=config.OLLAMA_BASE_URL,
            model=config.OLLAMA_MODEL,
            temperature=0.1
        )
        
        self.prompt = PromptTemplate(
            input_variables=["trade_id", "trader_id", "symbol", "quantity", "price", "timestamp", "order_type"],
            template=PROMPT_TEMPLATE
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def classify(self, transaction: Transaction) -> tuple[LlamaResult, float]:
        """
        Classify a transaction using LLM
        Returns: (LlamaResult, latency_ms)
        """
        start_time = time.time()
        
        try:
            # Call LLM
            response = self.chain.invoke({
                "trade_id": transaction.trade_id,
                "trader_id": transaction.trader_id,
                "symbol": transaction.symbol,
                "quantity": transaction.quantity,
                "price": transaction.price,
                "timestamp": transaction.timestamp,
                "order_type": transaction.order_type
            })
            
            # Parse response
            result_text = response.get("text", "")
            llama_result = self._parse_response(result_text)
            
            latency_ms = (time.time() - start_time) * 1000
            logger.info(f"Classified {transaction.trade_id} as {llama_result.label} in {latency_ms:.2f}ms")
            
            return llama_result, latency_ms
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            # Fallback: default to legit with low confidence
            latency_ms = (time.time() - start_time) * 1000
            return LlamaResult(
                label="legit",
                confidence=0.5,
                reason=f"Classification error: {str(e)}"
            ), latency_ms
    
    def _parse_response(self, response_text: str) -> LlamaResult:
        """
        Parse LLM response with robust error handling
        Enforces binary classification (fraud or legit)
        """
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            
            # Find JSON object in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON object found in response")
            
            json_str = response_text[start_idx:end_idx]
            parsed = json.loads(json_str)
            
            # Force label to be either "fraud" or "legit"
            label = parsed.get("label", "").lower()
            if label not in ["fraud", "legit"]:
                # Default to legit if ambiguous
                label = "legit" if parsed.get("confidence", 0.5) < 0.5 else "fraud"
            
            confidence = float(parsed.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
            
            reason = parsed.get("reason", "No reason provided")
            
            return LlamaResult(
                label=label,
                confidence=confidence,
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}. Response: {response_text}")
            # Fallback to legit with medium confidence
            return LlamaResult(
                label="legit",
                confidence=0.5,
                reason="Failed to parse LLM response"
            )

# Singleton instance
classifier = FraudClassifier()
