# 🔍 Real-Time Stock Market Fraud Detection System

An intelligent, real-time fraud detection system for stock market transactions using **AI-powered classification** with Llama3 LLM, event streaming with Kafka, and live visualization through WebSockets.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Performance](#performance)
- [License](#license)

---

## 🎯 Overview

This system simulates and detects fraudulent stock transactions in real-time for the **Indian National Stock Exchange (NSE)**. It combines modern streaming architecture with AI-powered fraud detection to provide instant classification of transactions as legitimate or fraudulent.

### What Does It Do?

1. **Generates** realistic stock market transactions for 15 Indian stocks (RELIANCE, TCS, INFY, etc.)
2. **Streams** transactions through Apache Kafka for scalable processing
3. **Classifies** each transaction using Llama3 LLM with confidence scores and reasoning
4. **Stores** all classifications in MongoDB with performance metadata
5. **Broadcasts** real-time updates to a React dashboard via WebSockets
6. **Visualizes** fraud patterns with interactive charts and filters

### Use Cases

- **Educational**: Learn event-driven architecture and AI integration
- **Demonstration**: Showcase real-time fraud detection capabilities
- **Research**: Experiment with LLM-based classification
- **Development**: Template for building production fraud detection systems

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    FRAUD DETECTION SYSTEM ARCHITECTURE                        │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌──────────────────────────────────────┐
│   PRODUCER      │         │         BACKEND SERVICES             │
│                 │         │                                      │
│  Transaction    │  Kafka  │  ┌────────────────────────────┐    │
│  Generator      │─Stream─>│  │  Flask API + SocketIO      │    │
│                 │         │  │  (app.py)                  │    │
│  - 15 NSE       │         │  └────────────────────────────┘    │
│    Stocks       │         │              ↓                      │
│  - Random       │         │  ┌────────────────────────────┐    │
│    Quantities   │         │  │  Kafka Consumer            │    │
│  - Price        │         │  │  (consumer.py)             │    │
│    Variations   │         │  │  - Retry Logic             │    │
│                 │         │  │  - Deduplication           │    │
│  Every 30s      │         │  │  - DLQ Handling           │    │
└─────────────────┘         │  └────────────────────────────┘    │
                            │              ↓                      │
                            │  ┌────────────────────────────┐    │
                            │  │  LLM Classifier            │    │
                            │  │  (llm_chain.py)            │    │
                            │  │  - Llama3 via Ollama       │    │
                            │  │  - Few-shot Prompting      │    │
                            │  │  - Binary Classification   │    │
                            │  └────────────────────────────┘    │
                            │              ↓                      │
                            │  ┌────────────────────────────┐    │
                            │  │  MongoDB Client            │    │
                            │  │  (db.py)                   │    │
                            │  │  - Atomic Updates          │    │
                            │  │  - Indexed Queries         │    │
                            │  └────────────────────────────┘    │
                            └──────────────────────────────────────┘
                                          ↓ WebSocket
                            ┌──────────────────────────────────────┐
                            │       FRONTEND (React)               │
                            │                                      │
                            │  ┌────────────────────────────┐    │
                            │  │  Dashboard                  │    │
                            │  │  - Real-time Counters       │    │
                            │  │  - Transaction Table        │    │
                            │  │  - Filtering                │    │
                            │  └────────────────────────────┘    │
                            └──────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                    │
├──────────────────┬──────────────────┬──────────────────┬───────────────────┤
│   Kafka          │   ZooKeeper      │   MongoDB        │   Ollama Llama3   │
│   (Confluent)    │   (Confluent)    │   (Database)     │   (LLM Engine)    │
│   Port: 9092     │   Port: 2181     │   Port: 27017    │   Port: 11434     │
└──────────────────┴──────────────────┴──────────────────┴───────────────────┘
```

### Data Flow

```
1. Producer generates transaction → TX00000001 (RELIANCE, 75000 shares, ₹8500)
                    ↓
2. Kafka streams to topic "transactions"
                    ↓
3. Consumer polls and validates with Pydantic
                    ↓
4. LLM analyzes: "Unusually large quantity suggests fraud"
                    ↓
5. Classification: { label: "fraud", confidence: 0.95, reason: "..." }
                    ↓
6. MongoDB stores: trade_classifications collection + update stats
                    ↓
7. WebSocket broadcasts to frontend
                    ↓
8. Dashboard updates in <280ms: Counters + Table refresh
```

---

## ✨ Key Features

### 🤖 AI-Powered Fraud Detection
- **Llama3 LLM** via Ollama for intelligent classification
- **Few-shot prompting** with domain-specific fraud indicators
- **Binary classification** (fraud/legit) with confidence scores (0-1)
- **Contextual reasoning** for each classification
- **Automatic fallback** on LLM errors

### 🔄 Robust Message Processing
- **Automatic retry** with exponential backoff (2s → 4s → 8s)
- **Dead Letter Queue (DLQ)** for failed messages
- **Deduplication** using trade_id tracking
- **Manual offset commits** for reliability
- **Transaction validation** with Pydantic schemas

### 📊 Live Dashboard
- **Real-time WebSocket updates** (<300ms latency)
- **Interactive statistics cards** with percentages
- **Color-coded transaction table** (green=legit, red=fraud)
- **Filtering** by fraud/legit status
- **Pagination** for historical data
- **Modern UI** with gradients and animations

### ⚡ Scalable Architecture
- **Kafka** for horizontal scalability and fault tolerance
- **MongoDB** with optimized indexes for fast queries
- **Containerized microservices** via Docker
- **Stateless backend** for easy scaling
- **Health checks** for all services

### 📈 Performance Tracking
- **LLM latency** measurement (~200-500ms)
- **End-to-end latency** tracking
- **Retry count** metadata
- **Transaction throughput** monitoring

### 🇮🇳 Indian Stock Market Focus
- **15 NSE stock symbols** (RELIANCE, TCS, HDFCBANK, INFY, etc.)
- **Realistic price ranges** in Indian Rupees (₹)
- **Market-specific fraud patterns**
- **Local timestamp** handling

---

## 🛠️ Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Primary language |
| **Flask** | 3.0.0 | Web framework |
| **Flask-SocketIO** | 5.3.5 | WebSocket support |
| **Kafka-Python** | 2.0.2 | Kafka client |
| **PyMongo** | 4.6.1 | MongoDB driver |
| **Pydantic** | 2.5.3 | Data validation |
| **LangChain** | 0.1.0 | LLM framework |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI library |
| **TypeScript** | 4.9.5 | Type safety |
| **Socket.IO Client** | 4.6.1 | WebSocket client |
| **React Scripts** | 5.0.1 | Build tools |

### Infrastructure

| Service | Version | Purpose |
|---------|---------|---------|
| **Kafka** | 7.5.0 (Confluent) | Message broker |
| **ZooKeeper** | Latest (Confluent) | Kafka coordination |
| **MongoDB** | Latest | NoSQL database |
| **Ollama** | Latest | LLM inference engine |
| **Docker** | Latest | Containerization |
| **Docker Compose** | Latest | Orchestration |

### AI Model

- **Llama3:8b** - Meta's 8 billion parameter LLM for fraud classification

---

## 📦 Prerequisites

Before running the system, ensure you have:

1. **Docker Desktop** - For running backend infrastructure
   - Download: https://www.docker.com/products/docker-desktop

2. **Ollama with Llama3** - Running locally on your machine
   ```bash
   # Install Ollama
   brew install ollama  # macOS

   # Pull Llama3 model (~4.7GB)
   ollama pull llama3:8b

   # Verify
   ollama list
   ```

3. **Node.js 16+** - For running the frontend
   ```bash
   node --version  # Should be 16.0.0 or higher
   ```

---

## 🚀 Quick Start

### Step 1: Start Ollama

Open Terminal 1:
```bash
ollama serve
```

Keep this terminal running.

---

### Step 2: Start Backend Infrastructure

Open Terminal 2:
```bash
# Navigate to project directory
cd "/path/to/Live-stock-trade-transactions-fraud-detection-solution"

# Start all backend services (Kafka, MongoDB, Backend, Producer)
./start-backend-only.sh
```

Wait until you see:
```
✨ Backend services are running!
```

This starts:
- ✅ **Kafka** + **ZooKeeper** (message streaming)
- ✅ **MongoDB** (database)
- ✅ **Backend API** (Flask + WebSocket on port 5001)
- ✅ **Producer** (generates transactions every 30s)

---

### Step 3: Start Frontend

Open Terminal 3:
```bash
cd frontend

# First time only: Install dependencies
npm install

# Start React development server
npm start
```

Browser automatically opens at: **http://localhost:3000**

---

### 🎉 You're Live!

You should see:
- 📊 **Real-time counters** updating every 30 seconds
- 📋 **Transaction table** with AI classifications
- ✅ **Green rows** for legitimate transactions
- 🚨 **Red rows** for fraudulent transactions
- 🎯 **Confidence scores** and AI reasoning

---

## 📁 Project Structure

```
fraud-detection-system/
│
├── backend/                          # Python Flask backend
│   ├── app.py                       # Flask app with REST API + WebSocket
│   ├── consumer.py                  # Kafka consumer with retry logic
│   ├── llm_chain.py                 # LangChain + Llama3 integration
│   ├── db.py                        # MongoDB client with indexes
│   ├── config.py                    # Centralized configuration
│   ├── schemas.py                   # Pydantic data models
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Backend container image
│   └── .dockerignore                # Docker build optimization
│
├── producer/                         # Transaction generator
│   ├── producer.py                  # Kafka producer with Indian stocks
│   └── Dockerfile                   # Producer container image
│
├── frontend/                         # React TypeScript frontend
│   ├── public/
│   │   └── index.html               # HTML template
│   ├── src/
│   │   ├── App.tsx                  # Main React component
│   │   ├── index.tsx                # React entry point
│   │   ├── index.css                # Global styles
│   │   ├── components/
│   │   │   ├── Counters.tsx         # Statistics cards
│   │   │   └── RecentTable.tsx      # Transaction history table
│   │   └── api/
│   │       └── socket.ts            # WebSocket client
│   ├── package.json                 # Node.js dependencies
│   ├── tsconfig.json                # TypeScript configuration
│   └── .dockerignore                # Docker build optimization
│
├── docker-compose-backend-only.yml  # Docker Compose configuration
├── start-backend-only.sh            # Startup script
├── .dockerignore                    # Root Docker ignore
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 🔄 How It Works

### 1. Transaction Generation (Producer)

The producer generates random transactions for 15 Indian NSE stocks:

**Stock Symbols:**
- RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK
- HINDUNILVR, BHARTIARTL, ITC, SBIN, LT
- BAJFINANCE, ASIANPAINT, MARUTI, TITAN, WIPRO

**Transaction Parameters:**
- **Quantity**: 10 to 100,000 shares (wide range for fraud detection)
- **Price**: 10% to 500% of normal range (creates legitimate and fraudulent patterns)
- **Traders**: 50 different trader IDs (T0001 - T0050)
- **Order Type**: Buy or Sell (randomly selected)

**Example Transaction:**
```json
{
  "trade_id": "TX00000123",
  "trader_id": "T0042",
  "symbol": "RELIANCE",
  "quantity": 75000,
  "price": 8500.50,
  "timestamp": "2025-11-08T10:30:00",
  "order_type": "buy"
}
```

---

### 2. Kafka Streaming

Transactions are sent to Kafka topic `transactions`:
- **Key**: trade_id (for partitioning)
- **Value**: JSON transaction object
- **Acknowledgment**: Waits for broker confirmation

**Why Kafka?**
- **Scalability**: Handle millions of transactions
- **Reliability**: Message persistence and replay
- **Decoupling**: Producer and consumer are independent

---

### 3. Consumer Processing

The Kafka consumer polls messages and processes them:

**Processing Steps:**

1. **Deduplication Check**
   - Skip if trade_id already processed

2. **Validation**
   - Validate transaction using Pydantic schema
   - Ensure all required fields are present

3. **Retry Loop** (up to 3 retries)
   - Attempt 1: Immediate
   - Attempt 2: Wait 2 seconds (2^1)
   - Attempt 3: Wait 4 seconds (2^2)
   - Attempt 4: Wait 8 seconds (2^3)

4. **LLM Classification**
   - Send to Llama3 for analysis
   - Measure latency

5. **Database Storage**
   - Insert classification document
   - Atomically update statistics

6. **WebSocket Broadcast**
   - Emit transaction to frontend
   - Emit updated statistics

7. **Commit Offset**
   - Mark message as processed

**Failure Handling:**
- After 3 failed retries, send to Dead Letter Queue (DLQ)
- Log error details
- Continue processing next message

---

### 4. LLM Classification

Llama3 analyzes transactions using few-shot prompting:

**Fraud Indicators:**
- Unusually large quantity (>50,000 shares) → Market manipulation
- Very high prices (>300% of typical range) → Pump schemes
- Very low prices (<50% of typical range) → Wash trading
- Extreme quantities with unusual patterns

**Legit Indicators:**
- Normal trading quantities (10-10,000 shares)
- Reasonable price ranges (50-150% of typical values)
- Standard trading patterns

**Example Classification:**
```json
{
  "label": "fraud",
  "confidence": 0.95,
  "reason": "Unusually large quantity of 75,000 shares suggests potential market manipulation"
}
```

**Response Processing:**
- Parse JSON from LLM response
- Enforce binary classification (fraud/legit only)
- Clamp confidence to [0.0, 1.0]
- Fallback to legit (0.5) on error

---

### 5. Database Persistence

MongoDB stores all classifications with metadata:

**Collections:**

1. **trade_classifications**
   - All classified transactions
   - Includes LLM result + latency metadata
   - Indexed on: trade_id (unique), timestamp, label

2. **stats**
   - Global counters: { total, legit, fraud }
   - Atomically updated on each classification

**Atomic Update Example:**
```javascript
db.stats.findOneAndUpdate(
  { "_id": "stats" },
  {
    $inc: { "total": 1, "fraud": 1 },
    $set: { "updated_at": new Date() }
  },
  { returnDocument: "after" }
)
```

---

### 6. Real-Time Visualization

Frontend receives updates via WebSocket:

**WebSocket Events:**

1. **summary_counts**
   ```json
   { "total": 1250, "legit": 1100, "fraud": 150 }
   ```

2. **transaction_stream**
   ```json
   {
     "trade_id": "TX00000123",
     "symbol": "RELIANCE",
     "label": "fraud",
     "confidence": 0.95,
     "reason": "...",
     ...
   }
   ```

**UI Updates:**
- **Counters**: Show percentages (Fraud: 12%, Legit: 88%)
- **Table**: Prepend new transaction (keep last 200)
- **Filters**: All / Legit / Fraud
- **Colors**: Red border for fraud, Green for legit

---

## 📡 API Documentation

### REST API Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

#### 2. Get Summary Statistics

```http
GET /api/summary
```

**Response:**
```json
{
  "total": 1250,
  "legit": 1100,
  "fraud": 150
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Database error

---

#### 3. Get Transactions (Paginated)

```http
GET /api/transactions?limit=100&skip=0&label=fraud
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Number of transactions to return |
| `skip` | integer | 0 | Offset for pagination |
| `label` | string | null | Filter by "fraud" or "legit" |

**Response:**
```json
{
  "transactions": [
    {
      "_id": "67...",
      "trade_id": "TX00000123",
      "trader_id": "T0042",
      "symbol": "RELIANCE",
      "quantity": 75000,
      "price": 8500.50,
      "timestamp": "2025-11-08T10:30:00",
      "order_type": "buy",
      "llama_result": {
        "label": "fraud",
        "confidence": 0.95,
        "reason": "Unusually large quantity suggests market manipulation"
      },
      "processed_at": "2025-11-08T10:30:01.234Z",
      "consumer_metadata": {
        "llm_latency_ms": 320.5,
        "end_to_end_latency_ms": 280.2,
        "retry_count": 0
      }
    }
  ],
  "count": 1,
  "limit": 100,
  "skip": 0,
  "label": "fraud"
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid label parameter
- `500 Internal Server Error` - Database error

---

### WebSocket Events

**Connection URL:** `http://localhost:5001`

#### Client → Server Events

**1. connect**
- Triggered automatically on connection
- Server responds with initial `summary_counts`

**2. disconnect**
- Triggered on disconnection

---

#### Server → Client Events

**1. summary_counts**

Emitted: On connect, after each classification

```json
{
  "total": 1250,
  "legit": 1100,
  "fraud": 150
}
```

---

**2. transaction_stream**

Emitted: After each classification

```json
{
  "trade_id": "TX00000123",
  "trader_id": "T0042",
  "symbol": "RELIANCE",
  "quantity": 75000,
  "price": 8500.50,
  "timestamp": "2025-11-08T10:30:00",
  "order_type": "buy",
  "label": "fraud",
  "confidence": 0.95,
  "reason": "Unusually large quantity suggests market manipulation",
  "processed_at": "2025-11-08T10:30:01.234Z"
}
```

---

## ⚙️ Configuration

### Environment Variables

All configuration is in `docker-compose-backend-only.yml` or `.env` file:

**Kafka Configuration:**
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka:29092    # Kafka broker address
KAFKA_TOPIC=transactions               # Main topic
KAFKA_DLQ_TOPIC=transactions_dlq       # Dead Letter Queue
KAFKA_GROUP_ID=fraud-detector-group    # Consumer group ID
```

**MongoDB Configuration:**
```bash
MONGO_URI=mongodb://mongodb:27017      # MongoDB connection string
MONGO_DB=fraud_detection               # Database name
```

**Ollama Configuration:**
```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Ollama API URL
OLLAMA_MODEL=llama3:8b                             # LLM model name
```

**Flask Configuration:**
```bash
FLASK_HOST=0.0.0.0              # Bind to all interfaces
FLASK_PORT=5000                 # Internal port (mapped to 5001 externally)
FLASK_DEBUG=False               # Debug mode (set to True for development)
CORS_ALLOWED_ORIGINS=*          # CORS allowed origins
```

**Retry Configuration:**
```bash
MAX_RETRIES=3                   # Maximum retry attempts
RETRY_BACKOFF_BASE=2.0          # Exponential backoff base (2^n seconds)
```

**Frontend Configuration:**

Edit `frontend/src/api/socket.ts`:
```typescript
const SOCKET_URL = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5001';
```

### Port Mapping

| Service | Container Port | Host Port | Access |
|---------|----------------|-----------|--------|
| **ZooKeeper** | 2181 | 2181 | Kafka coordination |
| **Kafka** | 29092, 9092 | 9092 | Message broker |
| **MongoDB** | 27017 | 27017 | Database |
| **Backend** | 5000 | **5001** | API + WebSocket |
| **Frontend** | 3000 | 3000 | React dev server |
| **Ollama** | 11434 | 11434 | LLM API (host machine) |

**Note:** Backend runs on port **5001** (not 5000) to avoid conflict with macOS AirPlay Receiver.

---

## 🗄️ Database Schema

### Collection: `trade_classifications`

**Purpose:** Store all classified transactions with metadata

**Document Structure:**
```javascript
{
  "_id": ObjectId("..."),
  "trade_id": "TX00000123",              // Unique identifier
  "trader_id": "T0042",
  "symbol": "RELIANCE",
  "quantity": 75000,
  "price": 8500.50,
  "timestamp": "2025-11-08T10:30:00",
  "order_type": "buy",
  "llama_result": {
    "label": "fraud",                    // "fraud" or "legit"
    "confidence": 0.95,                  // 0.0 to 1.0
    "reason": "Unusually large quantity suggests market manipulation"
  },
  "processed_at": "2025-11-08T10:30:01.234Z",
  "consumer_metadata": {
    "llm_latency_ms": 320.5,             // Time for LLM classification
    "end_to_end_latency_ms": 280.2,      // Total processing time
    "retry_count": 0                     // Number of retries (0-3)
  },
  "raw_message": { ... }                 // Optional: Original Kafka message
}
```

**Indexes:**
```javascript
// 1. Unique index on trade_id (prevents duplicates)
{ "trade_id": 1 } unique

// 2. Timestamp index (for recent queries)
{ "timestamp": -1 }

// 3. Compound index (for filtered queries)
{ "llama_result.label": 1, "timestamp": -1 }
```

---

### Collection: `stats`

**Purpose:** Store global fraud detection statistics

**Document Structure:**
```javascript
{
  "_id": "stats",                        // Fixed ID (single document)
  "total": 1250,                         // Total transactions
  "legit": 1100,                         // Legitimate count
  "fraud": 150,                          // Fraud count
  "updated_at": ISODate("2025-11-08T10:30:01Z")
}
```

**Atomic Updates:**

All stats updates use `findOneAndUpdate` with `$inc` to ensure atomicity:

```javascript
db.stats.findOneAndUpdate(
  { "_id": "stats" },
  {
    $inc: { "total": 1, "fraud": 1 },
    $set: { "updated_at": new Date() }
  },
  { returnDocument: "after" }
)
```

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

**Start Backend:**
```bash
cd backend
source venv/bin/activate  # Or create: python3 -m venv venv
python app.py
```

**Start Producer:**
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

---

### Viewing Logs

**All services:**
```bash
docker compose -f docker-compose-backend-only.yml logs -f
```

**Specific service:**
```bash
docker compose -f docker-compose-backend-only.yml logs -f backend
docker compose -f docker-compose-backend-only.yml logs -f producer
docker compose -f docker-compose-backend-only.yml logs -f kafka
```

**Last 50 lines:**
```bash
docker compose -f docker-compose-backend-only.yml logs --tail=50 backend
```

---

### Rebuilding After Code Changes

**Backend:**
```bash
docker compose -f docker-compose-backend-only.yml up -d --build backend
```

**Producer:**
```bash
docker compose -f docker-compose-backend-only.yml up -d --build producer
```

**All services:**
```bash
docker compose -f docker-compose-backend-only.yml up -d --build
```

---

### Accessing MongoDB

**Using Docker:**
```bash
docker exec -it fraud-detection-mongodb mongosh
```

**MongoDB Shell Commands:**
```javascript
// Switch to database
use fraud_detection

// View recent classifications
db.trade_classifications.find().sort({ timestamp: -1 }).limit(10)

// View statistics
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

// Find fraud transactions
db.trade_classifications.find(
  { "llama_result.label": "fraud" }
).sort({ timestamp: -1 }).limit(20)
```

---

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

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** Backend can't connect to Ollama
```bash
# Check if Ollama is running
curl http://localhost:11434

# If not, start it
ollama serve

# Verify model is available
ollama list | grep llama3
```

**Solution:** Make sure Ollama is running and `llama3:8b` model is pulled.

---

**Problem:** Kafka connection errors
```bash
# Check Kafka is running
docker compose -f docker-compose-backend-only.yml ps kafka

# Restart Kafka services
docker compose -f docker-compose-backend-only.yml restart zookeeper kafka

# Wait 30 seconds, then restart backend
docker compose -f docker-compose-backend-only.yml restart backend
```

---

**Problem:** MongoDB connection errors
```bash
# Check MongoDB is running
docker compose -f docker-compose-backend-only.yml ps mongodb

# View MongoDB logs
docker compose -f docker-compose-backend-only.yml logs mongodb

# Restart MongoDB
docker compose -f docker-compose-backend-only.yml restart mongodb
```

---

### Producer Issues

**Problem:** Producer not generating transactions
```bash
# Check producer logs
docker compose -f docker-compose-backend-only.yml logs producer

# Restart producer
docker compose -f docker-compose-backend-only.yml restart producer
```

---

### Frontend Issues

**Problem:** Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:5001/health

# Check browser console (F12) for WebSocket errors

# Verify socket URL in frontend/src/api/socket.ts
# Should be: http://localhost:5001
```

---

**Problem:** Frontend shows old data
```bash
# Clear browser cache and hard reload
# Chrome/Firefox: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

# Or fetch latest data
# Click on the Total counter to refresh
```

---

### Port Conflicts

**Problem:** Port already in use

```bash
# Find what's using the port
lsof -i :5001   # Backend
lsof -i :3000   # Frontend
lsof -i :9092   # Kafka
lsof -i :27017  # MongoDB

# Kill the process (replace <PID> with actual number)
kill -9 <PID>

# Or change port in docker-compose-backend-only.yml
```

**macOS AirPlay Receiver uses port 5000:**
- System Settings → General → AirDrop & Handoff → Turn off "AirPlay Receiver"
- Or keep using port 5001 (already configured)

---

### Reset Everything

**Stop and remove all data:**
```bash
docker compose -f docker-compose-backend-only.yml down -v
```

**Fresh start:**
```bash
./start-backend-only.sh
```

---

## 📈 Performance

### Latency Measurements

| Metric | Average | Description |
|--------|---------|-------------|
| **Transaction Generation** | 30s | Producer interval (configurable) |
| **Kafka Delivery** | <50ms | Producer to broker |
| **LLM Classification** | 200-500ms | Llama3 inference time |
| **MongoDB Write** | <10ms | Insert + update stats |
| **WebSocket Broadcast** | <5ms | Backend to frontend |
| **End-to-End** | ~280ms | Kafka to dashboard |

### Throughput

- **Current**: 2 transactions/minute (30s interval)
- **Configurable**: Change `interval` in `producer.py` line 173
  ```python
  producer.start(interval=10.0)  # 10 seconds = 6 tx/min
  ```

### Resource Usage

**Docker Containers:**
- Kafka: ~512MB RAM
- MongoDB: ~256MB RAM
- Backend: ~128MB RAM
- Producer: ~64MB RAM

**Ollama (Host):**
- Llama3:8b: ~4.7GB disk, ~2GB RAM during inference

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Built for educational purposes to demonstrate:
- Real-time fraud detection
- Event-driven architecture
- AI integration with LLMs
- Modern full-stack development

---

## 🙏 Acknowledgments

- **Meta AI** - Llama3 model
- **Ollama** - Local LLM inference
- **Confluent** - Kafka platform
- **MongoDB** - Database
- **LangChain** - LLM framework

---

## 📞 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review service logs: `docker compose -f docker-compose-backend-only.yml logs -f`
3. Verify all prerequisites are met
4. Ensure all ports are available

---

**🎉 Happy Fraud Detecting!**

Open **http://localhost:3000** and watch AI-powered fraud detection in action!
