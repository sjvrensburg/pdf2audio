#!/bin/bash

# PDF2Audio Setup Script
# This script clones the required open-source repositories

set -e

echo "🚀 Setting up PDF2Audio dependencies..."

# Create docker-services directory if it doesn't exist
mkdir -p docker-services

# Clone GROBID
if [ ! -d "docker-services/grobid" ]; then
    echo "📄 Cloning GROBID v0.8.0..."
    git clone --branch 0.8.0 --depth 1 https://github.com/kermitt2/grobid.git docker-services/grobid
else
    echo "✅ GROBID already exists"
fi

# Clone Speech Rule Engine
if [ ! -d "docker-services/speech-rule-engine" ]; then
    echo "🔢 Cloning MathJax Speech Rule Engine v4.0.0..."
    git clone --branch v4.0.0 --depth 1 https://github.com/zorkow/speech-rule-engine.git docker-services/speech-rule-engine
else
    echo "✅ Speech Rule Engine already exists"
fi

# Clone Piper TTS
if [ ! -d "docker-services/piper" ]; then
    echo "🎤 Cloning Piper TTS..."
    git clone --depth 1 https://github.com/rhasspy/piper.git docker-services/piper
else
    echo "✅ Piper TTS already exists"
fi

echo ""
echo "✅ All dependencies cloned successfully!"
echo ""
echo "📋 Next steps:"
echo "1. For development: docker compose -f docker-compose.dev.yml up --build"
echo "2. For production: docker compose up --build"
echo ""
echo "🌐 Access the application at:"
echo "   Frontend: http://localhost:12000"
echo "   Backend API: http://localhost:5000"
echo ""