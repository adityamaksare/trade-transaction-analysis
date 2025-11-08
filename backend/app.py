import logging
import threading
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

from config import config
from db import mongodb
from consumer import SparkFraudDetectionConsumer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fraud-detection-secret'
CORS(app, resources={r"/*": {"origins": config.CORS_ALLOWED_ORIGINS}})

# Initialize SocketIO with threading mode
socketio = SocketIO(
    app,
    cors_allowed_origins=config.CORS_ALLOWED_ORIGINS,
    async_mode=config.SOCKETIO_ASYNC_MODE
)

# Global consumer instance
consumer = None

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get current fraud detection stats"""
    try:
        stats = mongodb.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get paginated transaction history with optional filters"""
    try:
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))
        label = request.args.get('label', None)
        
        # Validate label
        if label and label not in ['fraud', 'legit']:
            return jsonify({"error": "Invalid label. Must be 'fraud' or 'legit'"}), 400
        
        transactions = mongodb.get_transactions(limit=limit, label=label, skip=skip)
        
        # Convert ObjectId to string for JSON serialization
        for tx in transactions:
            if '_id' in tx:
                tx['_id'] = str(tx['_id'])
        
        return jsonify({
            "transactions": transactions,
            "count": len(transactions),
            "limit": limit,
            "skip": skip,
            "label": label
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info('Client connected')
    
    # Send current stats on connect
    try:
        stats = mongodb.get_stats()
        socketio.emit('summary_counts', stats)
    except Exception as e:
        logger.error(f"Error sending initial stats: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

def start_consumer():
    """Start Spark Structured Streaming consumer in a separate thread"""
    global consumer
    try:
        consumer = SparkFraudDetectionConsumer(socketio=socketio)
        consumer.create_spark_session()
        consumer.start()
    except Exception as e:
        logger.error(f"Consumer thread error: {e}")

def main():
    """Main application entry point"""
    try:
        # Connect to MongoDB
        mongodb.connect()
        logger.info("MongoDB connected")
        
        # Start consumer in background thread
        consumer_thread = threading.Thread(target=start_consumer, daemon=True)
        consumer_thread.start()
        logger.info("Consumer thread started")
        
        # Start Flask app with SocketIO
        logger.info(f"Starting Flask app on {config.FLASK_HOST}:{config.FLASK_PORT}")
        socketio.run(
            app,
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG,
            allow_unsafe_werkzeug=True  # For development only
        )
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        # Cleanup
        if consumer:
            consumer.stop()
        mongodb.disconnect()
        logger.info("Application shutdown complete")

if __name__ == '__main__':
    main()
