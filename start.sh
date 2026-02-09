#!/bin/bash
set -e

echo "🚀 Launching Mami AI..."

# Start containers
docker-compose up -d

echo "✅ Services Started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Neo4j: http://localhost:7474"
