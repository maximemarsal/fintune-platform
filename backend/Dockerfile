FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    ffmpeg \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir --use-pep517 -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /tmp/uploads

# Expose the port
EXPOSE 8000

# Default port (Railway provides $PORT)
ENV PORT=8000

# Command to run the application (shell form to interpret $PORT)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 600 