FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY rag_api/ ./rag_api/

# Create storage directory structure
RUN mkdir -p /app/storage/data /app/storage/index

# Set environment variable for storage location
ENV STORAGE_DIR=/app/storage

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "8000"]