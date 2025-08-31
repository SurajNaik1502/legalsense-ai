#!/bin/bash

echo "🚀 LegalSense AI - Quick Start"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# OpenAI API Configuration (optional but recommended)
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
PROCESSED_DIR=processed
EOF
    echo "✅ Created .env file. Please edit it with your OpenAI API key if you have one."
fi

echo "🔧 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend failed to start. Check logs with: docker-compose logs backend"
fi

if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend failed to start. Check logs with: docker-compose logs frontend"
fi

echo ""
echo "🎉 LegalSense AI is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo ""
echo "🔍 Check the README.md for detailed usage instructions."
