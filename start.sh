#!/bin/bash

# SSO Consultant Enhanced - Production Start Script
# ================================================

# Exit immediately if a command exits with a non-zero status
set -e

# Set default environment variables
export PORT=${PORT:-10000}
export WORKERS=${WORKERS:-4}
export TIMEOUT=${TIMEOUT:-120}

# Load environment variables if .env exists
if [ -f /app/.env ]; then
    echo "🔧 Loading environment variables from .env"
    export $(grep -v '^#' /app/.env | xargs)
fi

echo "🚀 Starting SSO Consultant Enhanced"
echo "================================"

# Check for required environment variables
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ Error: DEEPSEEK_API_KEY environment variable is not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Install dependencies if not already installed
echo "📦 Checking Python dependencies..."
if [ -f "/app/requirements.txt" ]; then
    pip install --no-cache-dir -r /app/requirements.txt
else
    echo "⚠️  requirements.txt not found, skipping dependency installation"
fi

# Create necessary directories
echo "📂 Setting up directories..."
mkdir -p /app/data
chmod -R 755 /app/data

# Set proper permissions
echo "🔒 Setting permissions..."
chown -R appuser:appuser /app
chmod -R 755 /app

# Run database migrations if needed
# echo "🗄️ Running database migrations..."
# flask db upgrade

echo "✅ Initialization complete"

# Start the application
echo "🚀 Starting application server on port $PORT..."
echo "📊 Workers: $WORKERS | Timeout: $TIMEOUT seconds"

exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers $WORKERS \
    --timeout $TIMEOUT \
    --access-logfile - \
    --error-logfile - \
    --user appuser \
    --group appuser \
    sso_enhanced:app
