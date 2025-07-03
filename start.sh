#!/bin/bash

# PDF2Audio Startup Script
set -e

echo "🚀 Starting PDF2Audio Services..."
echo "=================================="

# Check if Docker is running
if ! sudo docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Starting Docker daemon..."
    sudo dockerd > /tmp/docker.log 2>&1 &
    sleep 10
fi

# Check Docker Compose
if ! command -v docker-compose >/dev/null 2>&1; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads temp

# Build and start services
echo "🔨 Building and starting services..."
sudo docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check Redis
if sudo docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not responding"
fi

# Check GROBID
if curl -s http://localhost:8070/api/isalive | grep -q true; then
    echo "✅ GROBID is healthy"
else
    echo "❌ GROBID is not responding"
fi

# Check Backend
if curl -s http://localhost:5000/health | grep -q healthy; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
fi

# Check Frontend
if curl -s http://localhost:12000 >/dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 PDF2Audio is ready!"
echo "=================================="
echo "📱 Frontend: http://localhost:12000"
echo "🔧 Backend API: http://localhost:5000"
echo "📄 GROBID: http://localhost:8070"
echo "🔊 Piper TTS: http://localhost:8080"
echo ""
echo "📋 To view logs: sudo docker-compose logs -f"
echo "🛑 To stop: sudo docker-compose down"
echo ""

# Show running containers
echo "📊 Running containers:"
sudo docker-compose ps