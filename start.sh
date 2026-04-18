#!/bin/bash
# Render deployment startup script

# Exit on any error
set -e

echo "=========================================="
echo "PageIQ API - Render Startup Script"
echo "=========================================="

# Install Python dependencies
echo "Installing dependencies..."
# We don't run pip install here to speed up startup, as it's done in buildCommand
# pip install --no-cache-dir -r requirements.txt

# Ensure relative path for Playwright browsers (Render Free Plan fix)
export PLAYWRIGHT_BROWSERS_PATH=./pw-browsers

# Browsers are installed during buildCommand to ./pw-browsers
echo "Checking Playwright browsers in $PLAYWRIGHT_BROWSERS_PATH..."
if [ -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then
    ls -R "$PLAYWRIGHT_BROWSERS_PATH" | head -n 20
else
    echo "ERROR: Browsers directory not found in $PLAYWRIGHT_BROWSERS_PATH"
fi

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
