# 🔍 AI-Powered Real-Time Stock Fraud Detection System

A production-grade, real-time fraud detection system for Indian stock market transactions using **Llama3 AI**, **PySpark Structured Streaming**, **Apache Kafka**, and **React**. Watch live as AI classifies transactions with 95%+ confidence in under 500ms.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PySpark](https://img.shields.io/badge/PySpark-3.5.0-orange.svg)](https://spark.apache.org/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://reactjs.org/)
[![Kafka](https://img.shields.io/badge/Kafka-7.5.0-black.svg)](https://kafka.apache.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Latest-green.svg)](https://www.mongodb.com/)
[![Llama3](https://img.shields.io/badge/Llama3-8B-purple.svg)](https://llama.meta.com/)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Development](#-development)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Author](#-author)

---

## 🎯 Overview

### What Does It Do?

This system simulates and detects fraudulent stock transactions in **real-time** for the **Indian National Stock Exchange (NSE)**. It combines modern streaming architecture with AI-powered fraud detection to provide instant classification of transactions.

**The Complete Flow:**
1. **Generates** realistic NSE stock transactions (RELIANCE, TCS, INFY, etc.) with intentional fraud patterns (~25%)
2. **Streams** transactions through Apache Kafka for scalable message delivery
3. **Processes** with PySpark Structured Streaming in 1-second micro-batches
4. **Classifies** using Llama3 (8B parameters) with few-shot prompting
5. **Stores** in MongoDB with performance metadata (latency, confidence, retries)
6. **Broadcasts** real-time updates to React dashboard via WebSocket
7. **Visualizes** fraud patterns with interactive filters and confidence scores

### Use Cases

- **Educational**: Learn event-driven architecture, stream processing, and AI integration
- **Demonstration**: Showcase real-time fraud detection capabilities to stakeholders
- **Research**: Experiment with LLM-based classification and prompt engineering
- **Development**: Production-ready template for building fraud detection systems

---

## 🎥 Live Demo

**What You'll See:**

- **Real-time Statistics**: Total, Legitimate, and Fraudulent transaction counters updating every 6 seconds (10 tx/min)
- **Live Transaction Stream**: New transactions appearing instantly with AI classifications via atomic WebSocket updates
- **Color-coded Rows**: Green for legitimate (✅), Red for fraudulent (⚠️)
- **Confidence Scores**: AI confidence levels (0-100%)
- **Reasoning**: Why each transaction was classified as fraud or legit
- **Interactive Filters**: Click cards or dropdown to filter by fraud/legit/all

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FRAUD DETECTION SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌────────────────────────────────────────────┐
│   PRODUCER       │         │         BACKEND SERVICES                   │
│                  │         │                                            │
│  Transaction     │  Kafka  │  ┌──────────────────────────────────┐    │
│  Generator       │─Stream─>│  │  Flask API + SocketIO            │    │
│                  │         │  │  - REST API (port 5001)          │    │
│  • 15 NSE Stocks │         │  │  - WebSocket Broadcasting        │    │
│  • Realistic     │         │  │  - CORS Enabled                  │    │
│    Price Ranges  │         │  └──────────────────────────────────┘    │
│  • Fraud         │         │                ↓                          │
│    Patterns      │         │  ┌──────────────────────────────────┐    │
│  • Every 6s      │         │  │  PySpark Streaming Consumer      │    │
│  • MongoDB ID    │         │  │  - 1-second micro-batches        │    │
│    Persistence   │         │  │  - Automatic checkpointing       │    │
│                  │         │  │  - Retry logic (3 attempts)      │    │
└──────────────────┘         │  │  - Deduplication tracking        │    │
                             │  └──────────────────────────────────┘    │
                             │                ↓                          │
                             │  ┌──────────────────────────────────┐    │
                             │  │  LLM Fraud Classifier            │    │
                             │  │  - Llama3 (8B) via Ollama        │    │
                             │  │  - Few-shot prompting            │    │
                             │  │  - Binary classification         │    │
                             │  │  - Latency: 200-500ms            │    │
                             │  └──────────────────────────────────┘    │
                             │                ↓                          │
                             │  ┌──────────────────────────────────┐    │
                             │  │  MongoDB Client                  │    │
                             │  │  - Dynamic stats calculation     │    │
                             │  │  - Indexed queries (processed_at)│    │
                             │  │  - Atomic upserts                │    │
                             │  └──────────────────────────────────┘    │
                             └────────────────────────────────────────────┘
                                           ↓ WebSocket
                             ┌────────────────────────────────────────────┐
                             │       FRONTEND (React + JavaScript)        │
                             │                                            │
                             │  ┌──────────────────────────────────┐    │
                             │  │  Real-time Dashboard             │    │
                             │  │  - Live counters with %          │    │
                             │  │  - Transaction history table     │    │
                             │  │  - Filtering (all/legit/fraud)   │    │
                             │  │  - Duplicate prevention          │    │
                             │  │  - Filter-aware WebSocket        │    │
                             │  └──────────────────────────────────┘    │
                             └────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                   │
├──────────────────┬──────────────────┬──────────────────┬──────────────────┤
│   Kafka          │   ZooKeeper      │   MongoDB        │   Ollama Llama3  │
│   (Confluent)    │   (Confluent)    │   (Database)     │   (LLM Engine)   │
│   Port: 9092     │   Port: 2181     │   Port: 27017    │   Port: 11434    │
└──────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

### Data Flow

```
Producer generates transaction
  ↓
  TX00000001: RELIANCE, 75000 shares @ ₹6,800 (buy)
  ↓
Kafka streams to topic "transactions"
  ↓
PySpark reads in 1-second micro-batch
  ↓
Validates with Pydantic schema
  ↓
LLM analyzes: "Price 2.5x typical range + large quantity = pump scheme"
  ↓
Classification: { label: "fraud", confidence: 0.95, reason: "..." }
  ↓
MongoDB stores + dynamic stats update
  ↓
WebSocket broadcasts to frontend
  ↓
Dashboard updates: Counters + New row in table (red border)
```

---

## ✨ Key Features

### 🤖 AI-Powered Fraud Detection

- **Llama3 (8B)** via Ollama for intelligent classification
- **Few-shot prompting** with NSE-specific fraud indicators
- **Binary classification** (fraud/legit) with confidence scores (0-1)
- **Contextual reasoning** explaining each decision
- **Price range validation** for all 15 NSE stocks
- **Automatic fallback** to "legit" on LLM errors

**Fraud Detection Rules:**
1. **Pump Scheme**: Price >4x typical range (e.g., INFY @ ₹6,400+ when range is ₹1,400-1,600)
2. **Wash Trading**: Price <0.4x typical AND quantity >70,000
3. **Market Manipulation**: Quantity >85,000 AND price >3.5x OR <0.4x typical

### 🔄 Robust Stream Processing (PySpark)

- **1-second micro-batches** for near-real-time processing
- **Structured Streaming** with Kafka connector (auto-downloads JARs)
- **Automatic checkpointing** at `./spark-checkpoint/` for fault tolerance
- **Exponential backoff retry** (2s → 4s → 8s, max 3 retries)
- **Deduplication** by trade_id to prevent duplicate processing
- **Dead Letter Queue** logging for failed transactions

### 📊 Modern React Dashboard

- **Atomic WebSocket updates** - Counter and table update simultaneously in single render cycle
- **Real-time updates** (<4s end-to-end latency from generation to display)
- **Interactive statistics cards** (click to filter transactions)
- **Color-coded table** with hover effects
- **Filter-aware WebSocket** (only shows matching transactions)
- **Duplicate prevention** (checks trade_id before adding)
- **Fetches ALL transactions** (up to 10,000 limit)
- **Mumbai timezone** display for processed_at
- **Pure JavaScript** implementation (no TypeScript overhead)

### ⚡ Scalable Architecture

- **PySpark** enables scaling from local (laptop) to distributed cluster without code changes
- **Kafka** provides horizontal scalability and fault tolerance
- **MongoDB** with optimized indexes on `processed_at` and `llama_result.label`
- **Containerized microservices** via Docker
- **Health checks** for all services (ZooKeeper, Kafka, MongoDB, Backend)
- **Dynamic stats calculation** ensures data consistency

### 📈 Performance Tracking

- **LLM latency** measurement (~200-500ms per transaction)
- **End-to-end latency** from Kafka to dashboard
- **Retry count** metadata for monitoring
- **Batch processing** metrics in Spark UI (http://localhost:4040)

### 🇮🇳 Indian Stock Market Focus

**15 NSE Stocks with Realistic Price Ranges (₹):**

| Symbol | Company | Typical Range |
|--------|---------|---------------|
| RELIANCE | Reliance Industries | ₹2,400-2,800 |
| TCS | Tata Consultancy Services | ₹3,500-4,000 |
| HDFCBANK | HDFC Bank | ₹1,500-1,700 |
| INFY | Infosys | ₹1,400-1,600 |
| ICICIBANK | ICICI Bank | ₹900-1,100 |
| HINDUNILVR | Hindustan Unilever | ₹2,300-2,600 |
| BHARTIARTL | Bharti Airtel | ₹800-1,000 |
| ITC | ITC Limited | ₹400-450 |
| SBIN | State Bank of India | ₹550-650 |
| LT | Larsen & Toubro | ₹3,200-3,600 |
| BAJFINANCE | Bajaj Finance | ₹6,500-7,500 |
| ASIANPAINT | Asian Paints | ₹2,800-3,200 |
| MARUTI | Maruti Suzuki | ₹10,000-12,000 |
| TITAN | Titan Company | ₹3,000-3,400 |
| WIPRO | Wipro | ₹400-500 |

---

## 🛠️ Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core language |
| PySpark | 3.5.0 | Distributed stream processing |
| Flask | 3.0.0 | Web framework |
| Flask-SocketIO | 5.3.5 | WebSocket support |
| Kafka-Python | 2.0.2 | Kafka producer |
| PyMongo | 4.6.1 | MongoDB driver |
| Pydantic | 2.5.3 | Data validation |
| LangChain | 0.1.0 | LLM framework |
| Java | 21 | PySpark JVM runtime |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI library |
| JavaScript | ES6+ | Core language (converted from TypeScript) |
| Socket.IO Client | 4.6.1 | WebSocket client |
| React Scripts | 5.0.1 | Build tooling |
| Bootstrap | 5.3.2 (CDN) | UI styling |

### Infrastructure

| Service | Version | Purpose |
|---------|---------|---------|
| Kafka | 7.5.0 (Confluent) | Message broker |
| ZooKeeper | Latest (Confluent) | Kafka coordination |
| MongoDB | Latest | NoSQL database |
| Ollama | Latest | LLM inference engine |
| Docker | Latest | Containerization |

### AI Model

- **Llama3:8b** - Meta's 8 billion parameter LLM (~4.7GB)

---

## 🚀 Quick Start

### Prerequisites

1. **Docker Desktop** - For backend infrastructure
   ```bash
   # Download: https://www.docker.com/products/docker-desktop
   docker --version  # Should show Docker version
   ```

2. **Ollama with Llama3** - Running on host machine
   ```bash
   # Install Ollama (macOS)
   brew install ollama

   # Pull Llama3 model (~4.7GB download)
   ollama pull llama3:8b

   # Verify
   ollama list | grep llama3
   ```

3. **Node.js 16+** - For frontend
   ```bash
   node --version  # Should be v16.0.0 or higher
   ```

### Step 1: Start Ollama

**Terminal 1:**
```bash
ollama serve
```

Keep this terminal running. You should see:
```
Ollama server listening on http://127.0.0.1:11434
```

### Step 2: Start Backend Services

**Terminal 2:**
```bash
# Navigate to project directory
cd /path/to/Live-stock-trade-transactions-fraud-detection-solution

# Make startup script executable (first time only)
chmod +x start-backend-only.sh

# Start all backend services
./start-backend-only.sh
```

Wait until you see:
```
✨ Backend services are running!
```

This starts:
- ✅ ZooKeeper (Kafka coordination)
- ✅ Kafka (message broker on port 9092)
- ✅ MongoDB (database on port 27017)
- ✅ Backend API (Flask + WebSocket on port 5001)
- ✅ Producer (generates 10 transactions/minute with MongoDB ID persistence)

### Step 3: Start Frontend

**Terminal 3:**
```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start React development server
npm start
```

Browser automatically opens at: **http://localhost:3000**

### 🎉 You're Live!

You should see:
- 📊 **Statistics Cards**: Total, Legitimate, Fraudulent (click to filter)
- 📋 **Transaction Table**: Real-time stream with AI classifications
- ✅ **Green rows**: Legitimate transactions
- ⚠️ **Red rows**: Fraudulent transactions
- 🎯 **Confidence scores**: 0-100% AI confidence
- 💡 **Reasoning**: Why AI classified each transaction

---

## 📁 Project Structure

```
fraud-detection-system/
│
├── backend/                          # Python backend (PySpark + Flask)
│   ├── app.py                       # Flask app with REST API + WebSocket
│   ├── consumer.py                  # PySpark Structured Streaming consumer
│   ├── llm_chain.py                 # LangChain + Llama3 integration
│   ├── db.py                        # MongoDB client with dynamic stats
│   ├── config.py                    # Configuration (Kafka, Spark, MongoDB, Ollama)
│   ├── schemas.py                   # Pydantic data models
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Container image (includes Java 21)
│   └── .dockerignore                # Docker build optimization
│
├── producer/                         # Transaction generator
│   ├── producer.py                  # Kafka producer (10 tx/min, ~25% fraud, MongoDB ID persistence)
│   └── Dockerfile                   # Producer container image
│
├── frontend/                         # React frontend (JavaScript)
│   ├── public/
│   │   └── index.html               # HTML template with Bootstrap CDN
│   ├── src/
│   │   ├── App.jsx                  # Main React component
│   │   ├── index.jsx                # React entry point
│   │   ├── index.css                # Global styles
│   │   ├── components/
│   │   │   ├── Counters.jsx         # Statistics cards (clickable)
│   │   │   └── RecentTable.jsx      # Transaction history table
│   │   └── api/
│   │       └── socket.js            # WebSocket client (duplicate prevention)
│   ├── package.json                 # Node.js dependencies (minimal)
│   ├── nginx.conf                   # Nginx config for production
│   └── Dockerfile                   # Frontend container image
│
├── docker-compose-backend-only.yml  # Docker Compose configuration
├── start-backend-only.sh            # Startup script with health checks
├── .dockerignore                    # Root Docker ignore
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🔄 How It Works

### 1. Transaction Generation (Producer)

The producer generates realistic transactions with **intentional fraud patterns** (~25%) and maintains **transaction ID persistence** via MongoDB:

**ID Persistence:**
- On startup, queries MongoDB for the highest `trade_id` (e.g., `TX00000567`)
- Extracts the counter value (567) and continues from there
- Prevents ID collisions and data loss across restarts
- Ensures transaction history grows continuously without resets

**Fraud Pattern Distribution:**
- **75%** - Normal/Legitimate: 100-75,000 shares, 0.6x-2.5x typical price
- **10%** - Pump Scheme: 5,000-95,000 shares, 4.5x-8.0x typical price
- **10%** - Wash Trading: 75,000-99,000 shares, 0.15x-0.35x typical price
- **5%** - Market Manipulation: 85,000-99,000 shares, 4.0x-7.0x OR 0.15x-0.35x typical price

**Example Transaction:**
```json
{
  "trade_id": "TX00000042",
  "trader_id": "T0023",
  "symbol": "RELIANCE",
  "quantity": 85000,
  "price": 6800.50,
  "timestamp": "2025-11-08T18:30:15",
  "order_type": "buy"
}
```

### 2. Kafka Streaming

Transactions flow through Kafka topic `transactions`:
- **Key**: trade_id (for partition distribution)
- **Value**: JSON transaction
- **Acknowledgment**: Waits for broker confirmation
- **Interval**: Every 6 seconds (10 transactions/minute)
- **ID Persistence**: Loads highest transaction ID from MongoDB on startup to maintain continuity

**Why Kafka?**
- **Scalability**: Handle millions of messages
- **Durability**: Persist messages for replay
- **Decoupling**: Producer and consumer are independent

### 3. PySpark Structured Streaming

PySpark processes transactions in **1-second micro-batches**:

**Processing Pipeline:**

1. **Spark Session Creation**
   - Downloads Kafka connector JAR (`spark-sql-kafka-0-10_2.12:3.5.0`)
   - Configures checkpoint directory for fault tolerance

2. **Stream Reading**
   - Reads from Kafka in streaming mode
   - Parses JSON into structured DataFrame

3. **Micro-Batch Trigger**
   - Triggers every 1 second
   - Collects all new messages

4. **Batch Processing** (`foreachBatch`)
   - Validates each transaction with Pydantic
   - Checks for duplicates (skip if trade_id already processed)
   - Retries up to 3 times with exponential backoff

5. **LLM Classification**
   - Sends to Llama3 for fraud analysis
   - Measures latency (~200-500ms)

6. **Database Storage**
   - Upserts classification to MongoDB
   - Calculates dynamic stats (counts actual documents)

7. **WebSocket Broadcast**
   - Emits transaction to frontend
   - Emits updated statistics

8. **Checkpointing**
   - Saves processing state to `./spark-checkpoint/`
   - Enables recovery from failures

**Failure Handling:**
- After 3 retries, logs to DLQ (error logs)
- Continues processing remaining messages in batch

### 4. LLM Classification

Llama3 analyzes transactions using **few-shot prompting**:

**Prompt Structure:**
```
You are a fraud detection expert analyzing Indian stock transactions.

TYPICAL PRICE RANGES (in ₹):
RELIANCE: ₹2,400-2,800 | TCS: ₹3,500-4,000 | ...

FRAUD INDICATORS:
1. Pump Scheme: Price >4x typical
2. Wash Trading: Price <0.4x typical AND quantity >70,000
3. Market Manipulation: Quantity >85,000 AND price >3.5x OR <0.4x

EXAMPLES:
✅ LEGIT: RELIANCE 75,000 @ ₹2,650 (within range)
❌ FRAUD: INFY 20,000 @ ₹7,000 (4.6x typical = pump scheme)

Transaction: RELIANCE 85,000 @ ₹6,800...

Respond with JSON:
{ "label": "fraud", "confidence": 0.95, "reason": "..." }
```

**Response Processing:**
- Parses JSON from LLM response
- Enforces binary classification (fraud/legit only)
- Clamps confidence to [0.0, 1.0]
- Fallback to "legit" (0.5 confidence) on errors

### 5. Database Persistence

MongoDB stores all classifications with metadata:

**Collection: `trade_classifications`**
```javascript
{
  "_id": ObjectId("..."),
  "trade_id": "TX00000042",
  "trader_id": "T0023",
  "symbol": "RELIANCE",
  "quantity": 85000,
  "price": 6800.50,
  "timestamp": "2025-11-08T18:30:15",
  "order_type": "buy",
  "llama_result": {
    "label": "fraud",
    "confidence": 0.95,
    "reason": "Large quantity (85,000) combined with price 2.4x typical range suggests market manipulation"
  },
  "processed_at": ISODate("2025-11-08T18:30:16.234Z"),
  "consumer_metadata": {
    "llm_latency_ms": 320.5,
    "end_to_end_latency_ms": 1250.2,
    "retry_count": 0
  }
}
```

**Collection: `stats`**
```javascript
{
  "_id": "stats",
  "total": 1250,      // Dynamically calculated on each query
  "legit": 950,       // count_documents({label: "legit"})
  "fraud": 300,       // count_documents({label: "fraud"})
  "updated_at": ISODate("2025-11-08T18:30:16Z")
}
```

**Indexes:**
- `trade_id` (unique) - Prevents duplicates
- `processed_at` (descending) - Fast sorting
- `llama_result.label, processed_at` (compound) - Fast filtered queries

### 6. Real-Time Visualization

Frontend receives updates via WebSocket:

**WebSocket Events:**

1. **`transaction_update`** - Primary atomic event emitted after each classification (NEW)
   ```json
   {
     "stats": { "total": 1250, "legit": 950, "fraud": 300 },
     "transaction": {
       "trade_id": "TX00000042",
       "symbol": "RELIANCE",
       "label": "fraud",
       "confidence": 0.95,
       "reason": "Large quantity combined with high price...",
       ...
     }
   }
   ```
   *Frontend updates both counter and transaction table atomically in one render cycle*

2. **`summary_counts`** - Emitted on connect and after each classification (backward compatibility)
   ```json
   { "total": 1250, "legit": 950, "fraud": 300 }
   ```

3. **`transaction_stream`** - Emitted after each classification (backward compatibility)
   ```json
   {
     "trade_id": "TX00000042",
     "symbol": "RELIANCE",
     "label": "fraud",
     "confidence": 0.95,
     "reason": "Large quantity combined with high price...",
     ...
   }
   ```

**UI Updates:**
- **Counters**: Show percentages (Fraud: 24%, Legit: 76%)
- **Table**: Prepends new transaction (keeps last 10,000)
- **Filters**: Click cards or dropdown to filter
- **Filter-aware**: Only adds transactions matching current filter
- **Duplicate prevention**: Checks trade_id before adding
- **Colors**: Red border for fraud, Green for legit

---

## 📡 API Reference

### REST API

**Base URL:** `http://localhost:5001`

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{ "status": "healthy" }
```

#### 2. Get Summary Statistics

```http
GET /api/summary
```

**Response:**
```json
{
  "total": 1250,
  "legit": 950,
  "fraud": 300
}
```

**Note:** Stats are **dynamically calculated** from actual MongoDB data on each request.

#### 3. Get Transactions (Paginated)

```http
GET /api/transactions?limit=100&skip=0&label=fraud
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Max transactions to return (max 10,000) |
| `skip` | integer | 0 | Offset for pagination |
| `label` | string | null | Filter by "fraud" or "legit" |

**Response:**
```json
{
  "transactions": [...],
  "count": 100,
  "limit": 100,
  "skip": 0,
  "label": "fraud"
}
```

### WebSocket API

**Connection URL:** `http://localhost:5001`

#### Client → Server Events

- **`connect`** - Automatic on connection (server responds with initial `summary_counts`)
- **`disconnect`** - Automatic on disconnection

#### Server → Client Events

- **`transaction_update`** - Primary atomic event combining stats and transaction (recommended)
- **`summary_counts`** - Emitted on connect and after each classification
- **`transaction_stream`** - Emitted after each classification

---

## ⚙️ Configuration

### Environment Variables

All configuration is in `docker-compose-backend-only.yml`:

**Kafka Configuration:**
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_TOPIC=transactions
KAFKA_DLQ_TOPIC=transactions_dlq
KAFKA_GROUP_ID=fraud-detector-group
```

**PySpark Configuration:**
```bash
SPARK_APP_NAME=FraudDetectionStreaming
SPARK_MASTER=local[*]                    # Use all CPU cores
SPARK_CHECKPOINT_DIR=./spark-checkpoint  # Fault tolerance
SPARK_KAFKA_OFFSET=earliest              # Read from start
SPARK_TRIGGER_INTERVAL=1 second          # Micro-batch interval
```

**MongoDB Configuration:**
```bash
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=fraud_detection
```

**Ollama Configuration:**
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Host machine
OLLAMA_MODEL=llama3:8b
```

**Flask Configuration:**
```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5000                  # Internal (mapped to 5001 externally)
FLASK_DEBUG=False
CORS_ALLOWED_ORIGINS=*
```

**Retry Configuration:**
```bash
MAX_RETRIES=3                    # Max retry attempts
RETRY_BACKOFF_BASE=2.0           # Exponential backoff (2^n seconds)
```

### Port Mapping

| Service | Container Port | Host Port | Access |
|---------|----------------|-----------|--------|
| ZooKeeper | 2181 | 2181 | Kafka coordination |
| Kafka | 29092 | 9092 | Message broker |
| MongoDB | 27017 | 27017 | Database |
| Backend | 5000 | **5001** | API + WebSocket |
| Frontend | 3000 | 3000 | React dev server |
| Ollama | 11434 | 11434 | LLM API (host) |

**Note:** Backend uses port **5001** to avoid conflict with macOS AirPlay Receiver (port 5000).

---

## 💻 Development

### Running Services Individually

**Start Kafka + ZooKeeper:**
```bash
docker compose -f docker-compose-backend-only.yml up -d zookeeper kafka
```

**Start MongoDB:**
```bash
docker compose -f docker-compose-backend-only.yml up -d mongodb
```

**Start Backend (Local Development):**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Start Producer (Local Development):**
```bash
cd producer
source ../backend/venv/bin/activate
python producer.py
```

**Start Frontend:**
```bash
cd frontend
npm start
```

### Viewing Logs

**All services:**
```bash
docker compose -f docker-compose-backend-only.yml logs -f
```

**Specific service:**
```bash
docker compose -f docker-compose-backend-only.yml logs -f backend
docker compose -f docker-compose-backend-only.yml logs -f producer
```

**Last 50 lines:**
```bash
docker compose -f docker-compose-backend-only.yml logs --tail=50 backend
```

**Grep for specific events:**
```bash
# View Spark batches
docker compose -f docker-compose-backend-only.yml logs backend | grep "Processing batch"

# View successful classifications
docker compose -f docker-compose-backend-only.yml logs backend | grep "Successfully processed"
```

### Monitoring PySpark

**Spark Web UI:**
```
http://localhost:4040
```

**What you can see:**
- Active streaming queries
- Batch processing times
- Input/output rates
- Memory usage
- Checkpoint status

### Accessing MongoDB

**Using Docker:**
```bash
docker exec -it fraud-detection-mongodb mongosh
```

**MongoDB Shell Commands:**
```javascript
// Switch to database
use fraud_detection

// View recent transactions
db.trade_classifications.find().sort({ processed_at: -1 }).limit(10)

// View stats
db.stats.findOne({ _id: "stats" })

// Count by label
db.trade_classifications.aggregate([
  { $group: {
      _id: "$llama_result.label",
      count: { $sum: 1 },
      avg_confidence: { $avg: "$llama_result.confidence" }
    }
  }
])

// Delete all transactions (reset)
db.trade_classifications.deleteMany({})
db.stats.updateOne(
  { _id: "stats" },
  { $set: { total: 0, legit: 0, fraud: 0 } }
)
```

### Testing Endpoints

**Health check:**
```bash
curl http://localhost:5001/health
```

**Get statistics:**
```bash
curl http://localhost:5001/api/summary | jq
```

**Get transactions:**
```bash
curl "http://localhost:5001/api/transactions?limit=5&label=fraud" | jq
```

### Rebuilding After Code Changes

**Backend:**
```bash
docker compose -f docker-compose-backend-only.yml up -d --build backend
```

**Producer:**
```bash
docker compose -f docker-compose-backend-only.yml up -d --build producer
```

**Frontend:**
```bash
cd frontend
npm start  # Auto-reloads on changes
```

---

## 📈 Performance

### Latency Measurements

| Metric | Average | Description |
|--------|---------|-------------|
| **Transaction Generation** | 6s | Producer interval (10 tx/min) |
| **Kafka Delivery** | <50ms | Producer to broker |
| **PySpark Micro-batch** | 1s | Batch trigger interval |
| **LLM Classification** | 2.5-3.5s | Llama3 inference (per tx) on M4 chip |
| **MongoDB Write** | <10ms | Insert + stats update |
| **WebSocket Broadcast** | <5ms | Backend to frontend (atomic updates) |
| **End-to-End** | ~3-4s | Kafka to dashboard |

### Throughput

- **Current**: 10 transactions/minute (6s interval)
- **Optimized for**: MacBook Air M4 chip with Llama3:8b
- **Configurable**: Change in `producer/producer.py:231`
  ```python
  producer.start(interval=6.0)   # 6s = 10 tx/min (current)
  producer.start(interval=3.0)   # 3s = 20 tx/min (aggressive)
  producer.start(interval=15.0)  # 15s = 4 tx/min (conservative)
  ```

**Performance Notes:**
- Processing time (~4s) < Generation interval (6s) = No queue buildup
- M4 chip handles 10 tx/min comfortably with plenty of headroom
- Can safely increase to 15-20 tx/min if needed

### Resource Usage

**Docker Containers:**
- Kafka: ~512MB RAM
- MongoDB: ~256MB RAM
- Backend (PySpark + Flask): ~400-600MB RAM
  - Java 21 JVM for PySpark
  - Spark executor memory
  - Python Flask process
- Producer: ~64MB RAM

**Ollama (Host):**
- Llama3:8b: ~4.7GB disk, ~2GB RAM during inference

**Frontend (Development):**
- React Dev Server: ~200MB RAM

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Backend can't connect to Ollama

```bash
# Check Ollama is running
curl http://localhost:11434

# Start Ollama
ollama serve

# Verify model
ollama list | grep llama3
```

**Problem:** PySpark can't start - Java gateway errors

```bash
# Check Java is installed in container
docker compose -f docker-compose-backend-only.yml exec backend java -version
# Should show: openjdk version "21"

# Rebuild if missing
docker compose -f docker-compose-backend-only.yml up -d --build backend
```

**Problem:** Kafka connection errors

```bash
# Restart Kafka services
docker compose -f docker-compose-backend-only.yml restart zookeeper kafka

# Wait 30 seconds, then restart backend
sleep 30
docker compose -f docker-compose-backend-only.yml restart backend
```

**Problem:** Spark checkpoint errors

```bash
# Remove corrupted checkpoint
docker compose -f docker-compose-backend-only.yml exec backend rm -rf ./spark-checkpoint

# Restart backend
docker compose -f docker-compose-backend-only.yml restart backend
```

### Producer Issues

**Problem:** Producer not generating transactions

```bash
# Check logs
docker compose -f docker-compose-backend-only.yml logs producer

# Restart
docker compose -f docker-compose-backend-only.yml restart producer
```

### Frontend Issues

**Problem:** Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:5001/health

# Check WebSocket URL in frontend/src/api/socket.js
# Should be: http://localhost:5001
```

**Problem:** Old data after refresh

```bash
# Click "Total Transactions" card to reload
# Or hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

### Port Conflicts

**Problem:** Port already in use

```bash
# Find what's using the port
lsof -i :5001   # Backend
lsof -i :3000   # Frontend
lsof -i :9092   # Kafka

# Kill the process
kill -9 <PID>
```

**macOS AirPlay Receiver (port 5000):**
- System Settings → General → AirDrop & Handoff → Turn off "AirPlay Receiver"
- Or keep using port 5001 (already configured)

### Reset Everything

**Stop and remove all data:**
```bash
docker compose -f docker-compose-backend-only.yml down -v
```

**Fresh start:**
```bash
./start-backend-only.sh
cd frontend && npm start  # In separate terminal
```

---

## 🚀 Why PySpark?

This system uses **PySpark Structured Streaming** for several key advantages:

### Scalability
- **Local to Distributed**: Run on laptop or multi-node cluster without code changes
- **Horizontal Scaling**: Add more Spark workers to handle increased load
- **Resource Management**: Efficient memory and CPU allocation

### Fault Tolerance
- **Automatic Checkpointing**: State saved periodically for crash recovery
- **Exactly-Once Semantics**: No duplicates or data loss
- **Task Retry**: Failed tasks automatically retried

### Performance
- **Micro-batch Processing**: Optimized for high-throughput streaming
- **Catalyst Optimizer**: SQL query optimization
- **Memory Management**: Efficient in-memory processing with spill to disk

### Production Ready
- **Battle-Tested**: Used by Netflix, Uber, Airbnb for large-scale streaming
- **Active Development**: Continuous improvements from Apache Spark community
- **Monitoring**: Built-in Spark UI for debugging and performance tuning

**Trade-off:** Slightly higher resource usage (~400MB vs ~128MB for simple Kafka consumer), but gains massive scalability and fault tolerance benefits.

---

## 👨‍💻 Author

**Aditya Maksare**

Built to demonstrate:
- Real-time fraud detection with AI
- Event-driven architecture with Kafka
- PySpark Structured Streaming for scalable data processing
- AI integration with LLMs (Llama3)
- Modern full-stack development (React + Flask)
- Microservices with Docker

---

## 🙏 Acknowledgments

- **Apache Spark** - Distributed stream processing engine
- **Meta AI** - Llama3 model
- **Ollama** - Local LLM inference
- **Confluent** - Kafka platform
- **MongoDB** - NoSQL database
- **LangChain** - LLM framework

---

## 📄 License

MIT License - Free to use for educational and commercial purposes

---

## 📞 Support

For issues:
1. Check [Troubleshooting](#-troubleshooting) section
2. View logs: `docker compose -f docker-compose-backend-only.yml logs -f`
3. Verify prerequisites are met
4. Ensure all ports are available

---

**🎉 Happy Fraud Detecting!**

Open **http://localhost:3000** and watch AI-powered fraud detection in action! 🚀
