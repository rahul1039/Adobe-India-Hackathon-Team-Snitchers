# Intelligent Document Analyst - Optimized for CPU-only execution
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and data
COPY . /app


# Set environment variables for optimal CPU performance
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Create output directory (optional, script creates its own)
RUN mkdir -p /app/outputs

# Run the document analyst
CMD ["python", "document_analyst.py"]
