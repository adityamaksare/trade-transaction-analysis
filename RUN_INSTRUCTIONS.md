# 🚀 COMPLETE RUN INSTRUCTIONS

Follow these steps **IN ORDER** to run the fraud detection system.

---

## ⚠️ PREREQUISITES (Install First)

Before starting, make sure you have:

1. **Java 8+** - Download from https://adoptium.net/
2. **Python 3.10+** - Check: `python --version`
3. **Node.js 16+** - Download from https://nodejs.org/
4. **MongoDB** - Download from https://www.mongodb.com/try/download/community
5. **Ollama** - Download from https://ollama.ai/

---

## 📝 STEP 1: Download & Setup Kafka

### 1.1 Download Kafka
1. Go to https://kafka.apache.org/downloads
2. Download **Binary downloads** (e.g., `kafka_2.13-3.6.0.tgz`)
3. Extract to **`C:\kafka`** (IMPORTANT: Use this exact path)

### 1.2 Verify Kafka Structure
After extraction, you should have:
```
C:\kafka\
  ├── bin\
  │   └── windows\
  ├── config\
  └── libs\
```

---

## 📝 STEP 2: Install & Setup Services

### 2.1 Install MongoDB
1. Install MongoDB using the MSI installer
2. During installation, check "Install MongoDB as a Service"
3. Verify it's running:
   ```powershell
   sc query MongoDB
   ```
   If not running:
   ```powershell
   net start MongoDB
   ```

### 2.2 Install Ollama & Pull Llama3
```powershell
# After installing Ollama from https://ollama.ai/
ollama pull llama3

# Verify
ollama list
```

---

## 📝 STEP 3: Install Project Dependencies

### 3.1 Create Virtual Environment & Install Python Dependencies
```powershell
cd "C:\Users\adity\OneDrive\Desktop\Live Stock Market Trade Transactions Fraud Detection Solution\backend"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2 Install Node.js Dependencies
```powershell
cd "C:\Users\adity\OneDrive\Desktop\Live Stock Market Trade Transactions Fraud Detection Solution\frontend"
npm install
```

---

## 🚀 STEP 4: START EVERYTHING (7 Windows)

Open **7 separate PowerShell windows** and run these commands:

### Window 1: Start ZooKeeper
```powershell
cd C:\kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```
**Wait** until you see: `"binding to port 0.0.0.0/0.0.0.0:2181"`

---

### Window 2: Start Kafka
```powershell
cd C:\kafka
.\bin\windows\kafka-server-start.bat .\config\server.properties
```
**Wait** until you see: `"Kafka Server started"`

---

### Window 3: Create Kafka Topic
```powershell
cd C:\kafka

# Create topic
.\bin\windows\kafka-topics.bat --create --topic transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Verify (you should see "transactions")
.\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```
**After creating the topic, you can close this window or keep it open to monitor**

---

### Window 4: Start Backend (Flask + Consumer)
```powershell
cd "C:\Users\adity\OneDrive\Desktop\Live Stock Market Trade Transactions Fraud Detection Solution\backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run backend
python app.py
```
**Wait** until you see: `"MongoDB connected"` and `"Starting Flask app..."`

---

### Window 5: Start Producer
```powershell
cd "C:\Users\adity\OneDrive\Desktop\Live Stock Market Trade Transactions Fraud Detection Solution\producer"

# Activate virtual environment (use backend's venv)
..\backend\venv\Scripts\Activate.ps1

# Run producer
python producer.py
```
**Wait** until you see: `"Starting transaction producer"`

---

### Window 6: Start Frontend
```powershell
cd "C:\Users\adity\OneDrive\Desktop\Live Stock Market Trade Transactions Fraud Detection Solution\frontend"
npm start
```
**Wait** for browser to open automatically at `http://localhost:3000`

---

### Window 7 (Optional): Monitor Kafka Messages
```powershell
cd C:\kafka
.\bin\windows\kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic transactions --from-beginning
```

---

## ✅ STEP 5: Verify Everything is Working

1. **Check ZooKeeper** (Window 1): Should show logs
2. **Check Kafka** (Window 2): Should show logs
3. **Check Backend** (Window 4): Should show `"MongoDB connected"` and `"Consumer thread started"`
4. **Check Producer** (Window 5): Should show `"Sent TX00000001 to transactions..."`
5. **Check Frontend** (Window 6): Browser should open to `http://localhost:3000`
6. **Dashboard**: You should see:
   - Transaction counters updating
   - Recent transactions table filling up
   - Real-time updates every 2 seconds

---

## 🔧 TROUBLESHOOTING

### Problem: "The input line is too long" (Kafka error)
**Solution**: Your Kafka path is too long or has spaces
```powershell
# Move Kafka to a simpler path
# Must be: C:\kafka (not C:\Program Files\kafka or other long paths)
```

### Problem: "Address already in use :9092" or ":2181"
**Solution**: Something is already running on those ports
```powershell
# Check what's using the port
netstat -ano | findstr :9092
netstat -ano | findstr :2181

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F
```

### Problem: MongoDB not connecting
**Solution**:
```powershell
# Check if MongoDB service is running
sc query MongoDB

# If not running, start it
net start MongoDB

# If service doesn't exist, create data directory and start manually
mkdir C:\data\db
mongod --dbpath C:\data\db
```

### Problem: Ollama not responding
**Solution**:
```powershell
# Check if Ollama is running
curl http://localhost:11434

# If not, start it
ollama serve

# Make sure llama3 is installed
ollama list
ollama pull llama3
```

### Problem: Python module not found
**Solution**:
```powershell
# Make sure you're in the backend directory
cd "C:\Users\adity\OneDrive\Desktop\Live Stock Market Trade Transactions Fraud Detection Solution\backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt

# If still failing, check Python version (need 3.10+)
python --version
```

### Problem: npm install fails
**Solution**:
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and retry
cd frontend
rm -r node_modules
npm install
```

### Problem: Frontend won't start
**Solution**:
```powershell
# Check if port 3000 is available
netstat -ano | findstr :3000

# If occupied, kill the process
taskkill /PID <PID> /F

# Try starting again
npm start
```

### Problem: Backend can't connect to Kafka
**Solution**:
1. Make sure ZooKeeper is running (Window 1)
2. Make sure Kafka is running (Window 2)
3. Make sure topic is created:
```powershell
cd C:\kafka
.\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```

### Problem: No transactions showing in dashboard
**Solution**:
1. Check Producer (Window 5) - should show "Sent TX..." messages
2. Check Backend (Window 4) - should show "Successfully processed..." messages
3. Check browser console (F12) - should show "WebSocket connected"
4. Refresh the browser page

---

## 🛑 HOW TO STOP EVERYTHING

1. **Frontend**: Press `Ctrl+C` in Window 6
2. **Producer**: Press `Ctrl+C` in Window 5
3. **Backend**: Press `Ctrl+C` in Window 4
4. **Kafka**: Press `Ctrl+C` in Window 2
5. **ZooKeeper**: Press `Ctrl+C` in Window 1
6. **MongoDB**: 
   ```powershell
   net stop MongoDB
   ```
7. **Ollama**: (Runs as service, doesn't need stopping)

---

## 📊 WHAT YOU SHOULD SEE

### In Producer Window (Window 5):
```
2025-10-30 13:48:00,123 - __main__ - INFO - Starting transaction producer (1 transaction every 2.0s)
2025-10-30 13:48:00,456 - __main__ - INFO - Sent TX00000001 to transactions partition 0 offset 0
2025-10-30 13:48:02,789 - __main__ - INFO - Sent TX00000002 to transactions partition 0 offset 1
```

### In Backend Window (Window 4):
```
2025-10-30 13:47:55,123 - __main__ - INFO - MongoDB connected
2025-10-30 13:47:55,456 - __main__ - INFO - Consumer thread started
2025-10-30 13:47:55,789 - __main__ - INFO - Starting Flask app on 0.0.0.0:5000
2025-10-30 13:48:00,234 - __main__ - INFO - Client connected
2025-10-30 13:48:01,567 - __main__ - INFO - Successfully processed TX00000001 - legit (0.85)
```

### In Dashboard (Browser):
- **Counters**: Total, Legit, Fraud numbers updating
- **Recent Transactions Table**: New rows appearing every 2 seconds
- **Transaction Details**: Trade ID, Trader, Symbol, Quantity, Price, Label, Confidence, Reason

---

## 🎯 QUICK TEST CHECKLIST

Before reporting issues, verify:

- [ ] Java is installed: `java -version`
- [ ] Python 3.10+: `python --version`
- [ ] Node.js installed: `node --version`
- [ ] Kafka extracted to: `C:\kafka`
- [ ] MongoDB service running: `sc query MongoDB`
- [ ] Ollama running: `curl http://localhost:11434`
- [ ] Llama3 model installed: `ollama list`
- [ ] Virtual environment created: `dir backend\venv`
- [ ] Python dependencies installed: Activate venv first, then `pip list | findstr kafka`
- [ ] Node dependencies installed: `dir frontend\node_modules`
- [ ] Kafka topic created: Check Window 3 output
- [ ] All 7 windows open and running
- [ ] Browser at http://localhost:3000

---

## 📞 GETTING HELP

If something still doesn't work:

1. **Take a screenshot** of the error in the PowerShell window
2. **Note which window/step** is failing
3. **Check the specific error message** and match it to troubleshooting section above

---

## 🔄 START ORDER SUMMARY

```
1. ZooKeeper      (Window 1) ← Start FIRST
2. Kafka          (Window 2) ← Wait for ZooKeeper
3. MongoDB        (Service)  ← Should already be running
4. Ollama         (Service)  ← Should already be running
5. Create Topic   (Window 3) ← Wait for Kafka
6. Backend        (Window 4) ← Wait for all above
7. Producer       (Window 5) ← Wait for Backend
8. Frontend       (Window 6) ← Can start anytime
```

---

## ✨ SUCCESS!

When everything is running correctly, you'll see:
- **Dashboard** updating every 2 seconds
- **Transaction counters** incrementing
- **New transactions** appearing in the table
- **Fraud/Legit labels** being assigned by AI
- **Real-time classification** with confidence scores

Enjoy your real-time fraud detection system! 🎉
