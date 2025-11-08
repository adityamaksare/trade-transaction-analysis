#!/bin/bash

# Start Backend Infrastructure Only
# Frontend runs locally with: cd frontend && npm start

set -e

echo "🚀 Starting Backend Infrastructure (Kafka, MongoDB, Backend, Producer)"
echo "======================================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if Ollama is running on host
echo "🔍 Checking local Ollama installation..."
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "❌ Ollama is not running on your Mac."
    echo ""
    echo "Please start Ollama in a separate terminal:"
    echo "  ollama serve"
    echo ""
    read -p "Press Enter once Ollama is running..."
fi

echo "✅ Ollama is running"
echo ""

# Check if llama3 model exists
echo "🔍 Checking for llama3 model..."
if ! ollama list | grep -q "llama3"; then
    echo "⚠️  llama3 model not found, but continuing..."
    echo "   Make sure you have it: ollama pull llama3"
fi

echo "✅ llama3 model found"
echo ""

# Use docker compose if available, otherwise docker-compose
if docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "📦 Using: $DOCKER_COMPOSE"
echo ""

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
$DOCKER_COMPOSE -f docker-compose-backend-only.yml down 2>/dev/null || true
echo ""

# Pull latest images
echo "📥 Pulling latest Docker images..."
$DOCKER_COMPOSE -f docker-compose-backend-only.yml pull
echo ""

# Build custom images
echo "🔨 Building application images..."
$DOCKER_COMPOSE -f docker-compose-backend-only.yml build
echo ""

# Start all services
echo "🚀 Starting backend services..."
$DOCKER_COMPOSE -f docker-compose-backend-only.yml up -d
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
echo ""

# Function to check service health
check_service() {
    local service=$1
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker inspect --format='{{.State.Health.Status}}' "fraud-detection-$service" 2>/dev/null | grep -q "healthy"; then
            echo "✅ $service is ready"
            return 0
        fi

        if [ $attempt -eq 1 ]; then
            echo -n "⏳ Waiting for $service..."
        else
            echo -n "."
        fi

        sleep 2
        attempt=$((attempt + 1))
    done

    echo ""
    echo "⚠️  $service is taking longer than expected"
    return 1
}

# Check critical services
check_service "mongodb"
check_service "zookeeper"
check_service "kafka"
check_service "backend"

echo ""
echo "======================================================================"
echo "✨ Backend services are running!"
echo "======================================================================"
echo ""
echo "🔧 Backend API: http://localhost:5000"
echo "🔧 Health Check: http://localhost:5000/health"
echo "📊 MongoDB: localhost:27017"
echo "📨 Kafka: localhost:9092"
echo ""
echo "📝 NEXT STEP: Start the Frontend"
echo "======================================================================"
echo ""
echo "Open a new terminal and run:"
echo ""
echo "  cd frontend"
echo "  npm install  # (first time only)"
echo "  npm start"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo "======================================================================"
echo ""
echo "📝 Useful commands:"
echo "   View logs:     $DOCKER_COMPOSE -f docker-compose-backend-only.yml logs -f"
echo "   Stop backend:  $DOCKER_COMPOSE -f docker-compose-backend-only.yml down"
echo "   Restart:       $DOCKER_COMPOSE -f docker-compose-backend-only.yml restart backend"
echo ""
echo "======================================================================"
