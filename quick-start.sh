#!/bin/bash

# AI Agent Platform Quick Start Script
# This script sets up and runs the AI Agent Platform

set -e

echo "🏡 AI Agent Platform - Quick Start"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${RED}❌ Please edit .env file and add your API keys before continuing${NC}"
    echo ""
    echo "Required API keys:"
    echo "  - ANTHROPIC_API_KEY (Claude)"
    echo "  - OPENAI_API_KEY (GPT-4)"
    echo "  - GROQ_API_KEY (Groq)"
    echo "  - MEM0_API_KEY (Memory)"
    echo "  - COMPOSIO_API_KEY (Integrations)"
    echo "  - REALESTATE_API_KEY (Property data)"
    echo ""
    echo "After adding keys, run this script again."
    exit 1
fi

echo "✅ Found .env file"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker Compose is installed"
echo ""

# Ask user for deployment method
echo "Choose deployment method:"
echo "1) Docker Compose (Recommended)"
echo "2) Local Python"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo ""
    echo "🐳 Starting with Docker Compose..."
    echo ""
    
    # Build and start services
    echo "Building Docker images..."
    docker-compose build
    
    echo ""
    echo "Starting services..."
    docker-compose up -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 5
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Services are running!${NC}"
        echo ""
        echo "📊 Service URLs:"
        echo "  - API: http://localhost:8000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - Health Check: http://localhost:8000/health"
        echo "  - WebSocket: ws://localhost:8000/ws/{user_id}"
        echo ""
        echo "📝 View logs:"
        echo "  docker-compose logs -f api"
        echo ""
        echo "🛑 Stop services:"
        echo "  docker-compose down"
    else
        echo -e "${RED}❌ Failed to start services${NC}"
        echo "Check logs with: docker-compose logs"
        exit 1
    fi

elif [ "$choice" == "2" ]; then
    echo ""
    echo "🐍 Starting with Local Python..."
    echo ""
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.11"
    
    if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
        echo -e "${YELLOW}⚠️  Python $PYTHON_VERSION found, but 3.11+ is recommended${NC}"
    else
        echo "✅ Python $PYTHON_VERSION found"
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo ""
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "✅ Virtual environment ready"
    
    # Activate virtual environment
    echo ""
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    echo ""
    echo "Installing dependencies..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    
    echo "✅ Dependencies installed"
    
    # Start PostgreSQL and Redis with Docker
    echo ""
    echo "Starting PostgreSQL and Redis..."
    docker-compose up -d postgres redis
    
    sleep 3
    
    # Start the application
    echo ""
    echo "🚀 Starting AI Agent Platform..."
    echo ""
    python -m backend.main
    
else
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
fi
