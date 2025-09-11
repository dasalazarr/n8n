#!/bin/bash

# SSO Consultant Enhanced - Production Start Script
# ================================================

# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "🔧 Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
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
echo "📦 Installing/updating Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create necessary directories
echo "📂 Setting up directories..."
mkdir -p /app/data

# Set proper permissions
echo "🔒 Setting permissions..."
chmod -R 755 /app

# Run database migrations if needed
# echo "🗄️ Running database migrations..."
# flask db upgrade

echo "✅ Initialization complete"

# Start the application
echo "🚀 Starting application server..."
exec gunicorn --bind 0.0.0.0:10000 --workers 4 --timeout 120 --access-logfile - --error-logfile - sso_enhanced:app
