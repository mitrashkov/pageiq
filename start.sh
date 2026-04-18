#!/bin/bash
# Render deployment startup script

# Exit on any error
set -e

echo "=========================================="
echo "PageIQ API - Render Startup Script"
echo "=========================================="

# Install Python dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies if not already present
echo "Ensuring Playwright browsers are installed..."
playwright install chromium --with-deps || python -m playwright install chromium --with-deps

# Create necessary directories
echo "Creating directories..."
mkdir -p data/screenshots
mkdir -p logs

# Run database migrations if needed
echo "Preparing database..."
python -m alembic upgrade head 2>/dev/null || echo "Database already up to date"

# Start the API server
echo "Starting PageIQ API on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'
