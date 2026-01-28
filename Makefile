.PHONY: help install start stop restart logs clean test build

# WebGenie Makefile
# Provides convenient commands for development and deployment

# Default target
help:
	@echo "WebGenie - Make Commands"
	@echo "=========================="
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install dependencies (frontend & backend)"
	@echo "  make start       - Start all services with Docker Compose"
	@echo "  make stop        - Stop all running services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services (use 'make logs-backend' for specific)"
	@echo "  make clean       - Remove all containers and volumes"
	@echo "  make dev         - Run backend in development mode"
	@echo ""
	@echo "Database:"
	@echo "  make migrate     - Run database migrations"
	@echo "  make db-shell    - Open PostgreSQL shell"
	@echo "  make db-reset    - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-backend - Run backend tests only"
	@echo "  make test-frontend - Run frontend tests only"
	@echo ""
	@echo "Building:"
	@echo "  make build       - Build Docker images"
	@echo "  make build-backend - Build backend image"
	@echo "  make build-frontend - Build frontend image"
	@echo ""
	@echo "Monitoring:"
	@echo "  make status      - Show service status"
	@echo "  make stats       - Show Docker resource usage"
	@echo ""
	@echo "API:"
	@echo "  make api-health  - Check backend health"
	@echo "  make api-datasets - List datasets"
	@echo "  make api-algorithms - List algorithms"
	@echo "  make api-jobs    - List jobs"
	@echo ""
	@echo "Deployment:"
	@echo "  make choreo-backend - Push backend to Choreo"
	@echo "  make choreo-frontend - Push frontend to Choreo"
	@echo ""

# Installation
install:
	@echo "Installing dependencies..."
	@cd webgenie-backend && pip install -r requirements.txt
	@cd ../webgenie-frontend && npm install
	@echo "✓ Dependencies installed"

install-backend:
	@echo "Installing backend dependencies..."
	@cd webgenie-backend && pip install -r requirements.txt
	@echo "✓ Backend dependencies installed"

install-frontend:
	@echo "Installing frontend dependencies..."
	@cd webgenie-frontend && npm install
	@echo "✓ Frontend dependencies installed"

# Docker Compose commands
start:
	@echo "Starting all services..."
	@docker-compose up -d
	@echo "✓ Services started"
	@echo "Frontend: http://localhost"
	@echo "Backend:  http://localhost:8000"
	@echo "Flower:   http://localhost:5555"

start-frontend:
	@echo "Starting frontend only..."
	@docker-compose up -d frontend

start-backend:
	@echo "Starting backend services..."
	@docker-compose up -d postgres redis backend celery_worker flower

stop:
	@echo "Stopping all services..."
	@docker-compose down
	@echo "✓ Services stopped"

restart:
	@echo "Restarting all services..."
	@docker-compose restart
	@echo "✓ Services restarted"

restart-backend:
	@docker-compose restart backend celery_worker

restart-frontend:
	@docker-compose restart frontend

logs:
	@docker-compose logs -f

logs-backend:
	@docker-compose logs -f backend

logs-frontend:
	@docker-compose logs -f frontend

logs-celery:
	@docker-compose logs -f celery_worker

logs-postgres:
	@docker-compose logs -f postgres

clean:
	@echo "Removing all containers and volumes..."
	@docker-compose down -v
	@rm -f .env
	@echo "✓ Clean complete"

# Development
dev:
	@cd webgenie-backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@cd webgenie-frontend && npm run dev

# Database operations
migrate:
	@echo "Running database migrations..."
	@docker-compose exec -T backend alembic upgrade head
	@echo "✓ Migrations complete"

db-shell:
	@docker-compose exec postgres psql -U webgenie -d webgenie_db

db-reset:
	@echo "WARNING: This will delete all data in the database!"
	@read -p "Are you sure? (yes/no): " confirm && \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose exec -T postgres psql -U webgenie -d webgenie_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		echo "✓ Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

db-backup:
	@echo "Backing up database..."
	@docker-compose exec -T postgres pg_dump -U webgenie webgenie_db > backups/webgenie_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup complete"

# Testing
test:
	@echo "Running all tests..."
	@docker-compose exec -T backend pytest -v

test-backend:
	@echo "Running backend tests..."
	@docker-compose exec -T backend pytest tests/ -v

test-backend-coverage:
	@docker-compose exec -T backend pytest tests/ --cov=app --cov-report=html

test-frontend:
	@cd webgenie-frontend && npm run test

# Building
build:
	@echo "Building all images..."
	@docker-compose build

build-backend:
	@echo "Building backend image..."
	@docker-compose build backend

build-frontend:
	@echo "Building frontend image..."
	@docker-compose build frontend

# Service status
status:
	@docker-compose ps

stats:
	@docker stats --no-stream

# API checks
api-health:
	@curl -s http://localhost:8000/health | jq .
	@echo ""

api-datasets:
	@curl -s http://localhost:8000/api/v1/datasets | jq .

api-algorithms:
	@curl -s http://localhost:8000/api/v1/algorithms | jq .

api-jobs:
	@curl -s http://localhost:8000/api/v1/jobs | jq .

# Linting and formatting
lint-backend:
	@cd webgenie-backend && flake8 app/ --max-line-length=120

format-backend:
	@cd webgenie-backend && black app/

lint-frontend:
	@cd webgenie-frontend && npm run lint

format-frontend:
	@cd webgenie-frontend && npm run format

# Docker cleanup
docker-clean:
	@echo "Cleaning up Docker..."
	@docker system prune -f
	@echo "✓ Docker cleanup complete"

# Choreo deployment
choreo-backend:
	@echo "Deploying backend to Choreo..."
	@git push choreo main
	@echo "Deployment initiated. Check Choreo console for progress."

choreo-frontend:
	@echo "Deploying frontend to Choreo..."
	@git push choreo-frontend main
	@echo "Deployment initiated. Check Choreo console for progress."

# Git operations
git-sync:
	@echo "Syncing with remote..."
	@git pull origin main
	@echo "✓ Synced"

git-commit:
	@read -p "Enter commit message: " msg && git add -A && git commit -m "$$msg"

git-push:
	@git push origin main
	@echo "✓ Pushed to remote"

# Documentation
docs:
	@echo "Opening documentation..."
	@open INTEGRATION_GUIDE.md || xdg-open INTEGRATION_GUIDE.md

docs-api:
	@open http://localhost:8000/docs

# Environment setup
env-local:
	@cp .env.local .env
	@echo "✓ Local environment configured"

env-prod:
	@cp .env.production .env
	@echo "✓ Production environment configured"

env-choreo:
	@cp .env.choreo .env
	@echo "✓ Choreo environment configured"
