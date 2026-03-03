FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn with Uvicorn workers
RUN pip install gunicorn

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs uploads/images uploads/voice

# Expose port
EXPOSE 80

# Run with Gunicorn (4 workers for better concurrency)
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:80"]
