#!/bin/bash

# WebGenie Quick Start Script
# This script sets up and starts the complete WebGenie stack locally

set -e

echo "🚀 WebGenie - Quick Start Setup"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Create necessary directories
echo -e "${BLUE}Creating data directories...${NC}"
mkdir -p /data/results
mkdir -p /data/datasets
mkdir -p /tmp/webgenie

echo -e "${GREEN}✓ Directories created${NC}"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from .env.local...${NC}"
    cp .env.local .env
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists${NC}"
fi

# Stop any existing containers
echo -e "${BLUE}Stopping existing containers...${NC}"
docker-compose down --remove-orphans 2>/dev/null || true

# Pull latest images
echo -e "${BLUE}Pulling Docker images...${NC}"
docker-compose pull

# Start services
echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${BLUE}Waiting for services to be ready...${NC}"
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "Waiting for backend... ($attempt/$max_attempts)"
    sleep 2
done

# Run database migrations
echo -e "${BLUE}Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head 2>/dev/null || echo "Database migration skipped"

# Display service information
echo ""
echo -e "${GREEN}=================================="
echo "✓ WebGenie Stack is Ready!"
echo "==================================${NC}"
echo ""
echo "📋 Service URLs:"
echo -e "${BLUE}Frontend:${NC}        http://localhost"
echo -e "${BLUE}Backend API:${NC}     http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}        http://localhost:8000/docs"
echo -e "${BLUE}Celery Flower:${NC}   http://localhost:5555"
echo -e "${BLUE}PgAdmin:${NC}         http://localhost:5050"
echo ""
echo "🐳 Running Services:"
docker-compose ps
echo ""
echo "📝 Useful Commands:"
echo "  View logs:      docker-compose logs -f backend"
echo "  Stop services:  docker-compose down"
echo "  List datasets:  curl http://localhost:8000/api/v1/datasets"
echo "  List algorithms: curl http://localhost:8000/api/v1/algorithms"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Open http://localhost in your browser"
echo "2. Upload or register a dataset"
echo "3. Submit a job using one of the algorithms"
echo "4. Monitor the job in Flower (http://localhost:5555)"
echo "5. View results when the job completes"
