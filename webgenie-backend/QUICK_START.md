# 🚀 Quick Start Guide - WebGenie Backend

Get the FastAPI backend running in minutes!

## Option 1: Docker Compose (Recommended) ⭐

The simplest way to get everything running:

```bash
cd webgenie-backend
docker-compose up -d
```

This starts:
- ✅ FastAPI backend (http://localhost:8000)
- ✅ Redis cache (localhost:6379)
- ✅ Celery worker (background jobs)
- ✅ Celery beat (scheduled tasks)
- ✅ Flower monitoring (http://localhost:5555)

**Access:**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Flower: http://localhost:5555

## Option 2: Local Development Setup

### Prerequisites
- Python 3.11+
- Redis (local or Docker)

### Setup

```bash
# Navigate to backend
cd webgenie-backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### Start Services (3 terminals)

**Terminal 1: Start Redis**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Terminal 2: FastAPI Server**
```bash
cd webgenie-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 3: Celery Worker**
```bash
cd webgenie-backend
source venv/bin/activate
celery -A app.core.tasks worker --loglevel=info
```

**Terminal 4 (optional): Celery Beat**
```bash
cd webgenie-backend
source venv/bin/activate
celery -A app.core.tasks beat --loglevel=info
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## First API Call

### Get Available Algorithms
```bash
curl http://localhost:8000/api/v1/algorithms
```

### Register a Dataset
```bash
curl -X POST http://localhost:8000/api/v1/datasets/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Dataset",
    "description": "A test dataset",
    "species": "Human",
    "tissue": "Liver",
    "source": {
      "source_type": "local",
      "url": "/data/test.csv",
      "metadata": {}
    },
    "schema": {
      "gene_column": "Gene",
      "cell_column": "Cell",
      "expression_column": "Expression"
    }
  }'
```

### Submit an Inference Job
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "test-dataset-xyz",
    "algorithm": "GRNBOOST2",
    "parameters": {
      "alpha": 0.5
    },
    "name": "My First Job"
  }'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/jobs/job-abc123
```

## 📚 Documentation

- **Full README**: [README.md](README.md)
- **Frontend Integration**: [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md)
- **API Docs**: http://localhost:8000/docs (interactive)
- **Implementation Details**: [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)

## 🔧 Configuration

Edit `.env` to configure:

```env
# Server
DEBUG=False
LOG_LEVEL=INFO

# Redis
REDIS_URL=redis://localhost:6379/0

# Algorithms
USE_DOCKER=True
MAX_CONCURRENT_JOBS=4
```

## 🆘 Troubleshooting

**Issue: Redis connection refused**
```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine
```

**Issue: Port already in use**
```bash
# Change port in docker-compose.yml or .env
SERVER_PORT=8001
```

**Issue: Module not found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Monitoring

**View Logs**
```bash
docker-compose logs -f backend
```

**Check Services**
```bash
docker-compose ps
```

**Stop All Services**
```bash
docker-compose down
```

## 🎯 Next Steps

1. ✅ Start the backend (Docker Compose is easiest)
2. ✅ Access API docs at http://localhost:8000/docs
3. ✅ Register a dataset
4. ✅ Submit an inference job
5. ✅ Monitor job progress
6. ✅ Download results

## 📞 Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md) for integration examples
- See [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) for feature details

---

**You're all set!** 🎉 The backend is running and ready for use.

Start with the interactive API docs at: http://localhost:8000/docs
