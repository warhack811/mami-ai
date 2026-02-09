#!/bin/bash
set -e

echo "🚀 Starting Mami AI Setup..."

# Copy env example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API Keys!"
fi

# Build Docker containers
echo "Building Docker containers..."
docker-compose build

echo "✅ Setup Complete! Run './start.sh' to launch."
