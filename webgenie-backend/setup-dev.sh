#!/bin/bash
# Startup script for development environment

set -e

echo "========================================="
echo "WebGenie Backend - Development Setup"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Copy .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created. Please update with your configuration.${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p /data/results /data/datasets /var/log/webgenie 2>/dev/null || true
mkdir -p logs

# Check Redis
echo -e "${YELLOW}Checking Redis connection...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}Redis is running${NC}"
else
    echo -e "${RED}Redis is not running${NC}"
    echo -e "${YELLOW}Starting Redis in background...${NC}"
    docker run -d -p 6379:6379 --name redis-webgenie redis:7-alpine || echo "Redis container might already exist"
fi

# Display next steps
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Start FastAPI server:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Start Celery worker (in another terminal):"
echo "   celery -A app.core.tasks worker --loglevel=info"
echo ""
echo "3. Start Celery beat (in another terminal):"
echo "   celery -A app.core.tasks beat --loglevel=info"
echo ""
echo "4. Access the API:"
echo "   http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
