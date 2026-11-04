# ShopSmart AI - Dockerfile for Containerized Cloud Deployment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Set working directory
WORKDIR /app

# Install system dependencies (build-essential, sqlite3)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project files
COPY . .

# Run ETL pipeline to prepare SQLite database
RUN python etl_pipeline.py

# Expose web port
EXPOSE 5000

# Start Flask with Gunicorn WSGI
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "app:app"]
