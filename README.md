# 🔍 Real-Time Fraud Detection System

A real-time stock market transaction fraud detection solution using Kafka, Ollama Llama3, MongoDB, Flask, and React.

## Architecture Overview

```
Producer (Python) → Kafka → Consumer (Flask) → LangChain/Llama3 → MongoDB
                                      ↓
                              WebSocket (SocketIO)
                                      ↓
                              React Dashboard
```

## Features

- ✅ Real-time transaction streaming via Kafka
- ✅ AI-powered fraud detection using Ollama Llama3
- ✅ Live dashboard with WebSocket updates
- ✅ MongoDB persistence with indexes
- ✅ Automatic retry logic with exponential backoff
- ✅ Dead Letter Queue (DLQ) for failed messages
- ✅ REST API for historical data
- ✅ Responsive React UI with filtering

## Prerequisites

1. **Python 3.10+**
2. **Node.js 16+**
3. **Kafka & ZooKeeper** (or Docker)
4. **MongoDB** (or Docker)
5. **Ollama** with Llama3 model

## Quick Start

### 1. Install Ollama & Pull Llama3

```bash
# Install Ollama from https://ollama.ai/
# Then pull the llama3 model
ollama pull llama3

# Verify it's running
ollama list
```

### 2. Start Kafka & ZooKeeper

#### Option A: Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
```

Run:
```bash
docker-compose up -d
```

#### Option B: Local Installation

Follow Kafka and MongoDB installation guides for your OS.

### 3. Create Kafka Topic

```bash
# If using Docker:
docker exec -it <kafka-container-id> kafka-topics --create --topic transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# If local Kafka:
kafka-topics.sh --create --topic transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 4. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 6. Run the Application

Open **4 terminal windows**:

#### Terminal 1: Start Backend (Flask + Consumer)
```bash
cd backend
python app.py
```

#### Terminal 2: Start Producer
```bash
cd producer
python producer.py
```

#### Terminal 3: Start Frontend
```bash
cd frontend
npm start
```

#### Terminal 4 (Optional): Monitor Kafka
```bash
# If using Docker:
docker exec -it <kafka-container-id> kafka-console-consumer --bootstrap-server localhost:9092 --topic transactions --from-beginning

# If local Kafka:
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions --from-beginning
```

### 7. Access the Dashboard

Open your browser and navigate to:
```
http://localhost:3000
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=transactions
KAFKA_GROUP_ID=fraud-detector-group

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=fraud_detection

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# CORS
CORS_ALLOWED_ORIGINS=*
```

## Project Structure

```
.
├── backend/
│   ├── app.py              # Flask app with WebSocket
│   ├── consumer.py         # Kafka consumer
│   ├── llm_chain.py        # LangChain + Llama3 integration
│   ├── schemas.py          # Pydantic models
│   ├── db.py               # MongoDB client
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
├── producer/
│   └── producer.py         # Kafka producer (generates fake data)
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main React app
│   │   ├── components/
│   │   │   ├── Counters.tsx
│   │   │   └── RecentTable.tsx
│   │   └── api/
│   │       └── socket.ts   # WebSocket client
│   └── package.json
└── README.md
```

## API Endpoints

### REST API

- `GET /health` - Health check
- `GET /api/summary` - Get current stats (total, legit, fraud)
- `GET /api/transactions?limit=100&label=fraud` - Get paginated transactions

### WebSocket Events

**Inbound:**
- `connect` - Client connects
- `disconnect` - Client disconnects

**Outbound:**
- `summary_counts` - `{ total, legit, fraud }`
- `transaction_stream` - Latest classified transaction

## Data Flow

1. **Producer** generates transaction → Kafka topic `transactions`
2. **Consumer** reads from Kafka → validates transaction
3. **LangChain** calls Ollama Llama3 → classifies as fraud/legit
4. **MongoDB** stores classification + updates stats
5. **WebSocket** emits to connected clients
6. **React Dashboard** updates in real-time

## MongoDB Schema

### Collection: `trade_classifications`

```json
{
  "trade_id": "TX00000001",
  "trader_id": "T0001",
  "symbol": "AAPL",
  "quantity": 100,
  "price": 150.50,
  "timestamp": "2025-10-30T08:00:00Z",
  "order_type": "buy",
  "llama_result": {
    "label": "legit",
    "confidence": 0.95,
    "reason": "Normal trading pattern"
  },
  "processed_at": "2025-10-30T08:00:01Z",
  "consumer_metadata": {
    "llm_latency_ms": 250.5,
    "end_to_end_latency_ms": 280.3,
    "retry_count": 0
  }
}
```

### Collection: `stats`

```json
{
  "_id": "stats",
  "total": 1000,
  "legit": 900,
  "fraud": 100,
  "updated_at": "2025-10-30T08:00:00Z"
}
```

## Troubleshooting

### Kafka Connection Issues
```bash
# Check if Kafka is running
docker ps  # or
netstat -an | grep 9092
```

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
docker ps  # or
netstat -an | grep 27017
```

### Ollama Issues
```bash
# Check if Ollama is running
ollama list

# Start Ollama service (if not running)
ollama serve
```

### LLM Classification Errors
- Ensure Ollama is running on `http://localhost:11434`
- Check that `llama3` model is pulled: `ollama pull llama3`
- Monitor backend logs for detailed error messages

## Performance Considerations

- **Transaction Rate**: Producer generates 1 transaction every 2 seconds (configurable)
- **LLM Latency**: ~200-500ms per classification (depends on hardware)
- **WebSocket**: No batching, immediate emission per transaction
- **MongoDB**: Indexed on `trade_id`, `timestamp`, and `label`
- **Memory**: Frontend keeps last 200 transactions in-memory

## Future Enhancements

- [ ] Add authentication for WebSocket and REST API
- [ ] Implement time-series charts for fraud trends
- [ ] Add advanced filtering (by trader, symbol, date range)
- [ ] Export data to CSV/Excel
- [ ] Alert system for high-fraud-rate periods
- [ ] Model performance metrics dashboard
- [ ] A/B testing different LLM models

## License

MIT

## Author

Built for educational purposes to demonstrate real-time fraud detection using modern data streaming and AI technologies.
