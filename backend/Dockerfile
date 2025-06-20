# Use PyTorch base image with CUDA support for AI models
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    libspatialindex-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install additional AI dependencies that might have conflicts
RUN pip install --no-cache-dir \
    'accelerate>=0.24.0' \
    'huggingface-hub>=0.19.0' \
    'safetensors>=0.4.0'

# Copy the rest of the application
COPY . .

# Create directories for model caching
RUN mkdir -p /app/models /app/cache

# Set environment variables for model caching
ENV TRANSFORMERS_CACHE=/app/cache
ENV HF_HOME=/app/cache
ENV TORCH_HOME=/app/models

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

