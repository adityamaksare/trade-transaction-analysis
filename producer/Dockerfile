# Producer Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements (producer uses same dependencies)
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create backend module directory and add __init__.py
RUN mkdir -p /app/backend && touch /app/backend/__init__.py

# Copy backend config and schemas (producer imports these)
COPY backend/config.py /app/backend/
COPY backend/schemas.py /app/backend/

# Copy producer code
COPY producer/producer.py .

# Run the producer
CMD ["python", "producer.py"]
