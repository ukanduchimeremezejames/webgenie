# WebGenie Backend - FastAPI Gene Regulatory Network Inference Platform

Production-ready FastAPI backend for the Beeline gene regulatory network inference platform. Exposes 14 GRN inference algorithms through RESTful APIs with asynchronous job orchestration using Celery.

## 🎯 Features

- **14 GRN Algorithms**: SCODE, SCNS, SINCERITIES, PIDC, GRNVBEM, GENIE3, GRNBOOST2, LEAP, JUMP3, PPCOR, GRISLI, SINGE, SCRIBE, SCSGL
- **Asynchronous Execution**: Celery-based job queue with Redis
- **Dataset Management**: Register, manage, and preview datasets
- **Job Management**: Submit, monitor, and cancel inference jobs
- **Results Analysis**: Network comparison, metric computation, multi-format export
- **RESTful API**: Complete API documentation via Swagger/OpenAPI
- **Docker Support**: Run algorithms in isolated containers
- **Monitoring**: Flower dashboard for task monitoring
- **Comprehensive Logging**: JSON-structured logging with context

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Redis (for task queue)
- 8GB+ RAM recommended

## 🚀 Quick Start

### Development Setup

```bash
# Clone repository
cd Beeline-master/webgenie-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start Redis (in another terminal)
docker run -d -p 6379:6379 redis:7-alpine

# Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.core.tasks worker --loglevel=info

# In another terminal, start Celery beat (for scheduled tasks)
celery -A app.core.tasks beat --loglevel=info
```

### Docker Compose (Recommended for Production)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

## 📚 API Documentation

Once running, access:
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Flower Dashboard**: http://localhost:5555

## 🔌 API Endpoints

### Datasets
```bash
POST   /api/v1/datasets/register        # Register new dataset
GET    /api/v1/datasets                 # List datasets
GET    /api/v1/datasets/{dataset_id}    # Get dataset details
GET    /api/v1/datasets/{dataset_id}/preview  # Preview dataset
PATCH  /api/v1/datasets/{dataset_id}    # Update dataset metadata
DELETE /api/v1/datasets/{dataset_id}    # Delete dataset
```

### Jobs
```bash
POST   /api/v1/jobs                     # Submit inference job
GET    /api/v1/jobs                     # List jobs (with filters)
GET    /api/v1/jobs/{job_id}            # Get job status
GET    /api/v1/jobs/{job_id}/logs       # Get job logs
DELETE /api/v1/jobs/{job_id}            # Cancel job
```

### Results
```bash
GET    /api/v1/results/job/{job_id}     # Get result
GET    /api/v1/results/job/{job_id}/summary        # Get result summary
POST   /api/v1/results/compare          # Compare two networks
GET    /api/v1/results/job/{job_id}/network/download  # Download network
POST   /api/v1/results/job/{job_id}/export  # Export results
```

### System
```bash
GET    /                                # Root info
GET    /health                          # Health check
GET    /api/v1/algorithms               # List available algorithms
```

## 📖 Usage Examples

### Register a Dataset
```bash
curl -X POST http://localhost:8000/api/v1/datasets/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Dataset",
    "description": "Single-cell expression data",
    "species": "Human",
    "tissue": "Liver",
    "source": {
      "source_type": "huggingface",
      "url": "cskokgibbs/datasets-GSD",
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
    "dataset_id": "my-dataset-xyz",
    "algorithm": "GRNBOOST2",
    "parameters": {
      "alpha": 0.5,
      "verbose": true
    },
    "name": "GRN Inference Run 1",
    "description": "Testing GRNBOOST2 on liver cells"
  }'
```

### Monitor Job Status
```bash
curl http://localhost:8000/api/v1/jobs/job-abc123
```

### Get Job Logs
```bash
curl http://localhost:8000/api/v1/jobs/job-abc123/logs
```

### Compare Two Networks
```bash
curl -X POST http://localhost:8000/api/v1/results/compare \
  -H "Content-Type: application/json" \
  -d '{
    "job_id_1": "job-abc123",
    "job_id_2": "job-def456"
  }'
```

## 🏗️ Project Structure

```
webgenie-backend/
├── app/
│   ├── main.py                    # FastAPI application
│   ├── core/
│   │   ├── config.py             # Configuration management
│   │   ├── logging.py            # Logging setup
│   │   └── tasks.py              # Celery configuration
│   ├── api/
│   │   ├── datasets.py           # Dataset endpoints
│   │   ├── jobs.py               # Job management endpoints
│   │   └── results.py            # Results endpoints
│   ├── services/
│   │   ├── datasets_service.py   # Dataset business logic
│   │   ├── inference_service.py  # Inference orchestration
│   │   ├── jobs_service.py       # Job management logic
│   │   └── runners/
│   │       ├── utils.py          # Runner utilities
│   │       ├── generic_runner.py # Generic GRN runner
│   │       └── ...               # Algorithm-specific runners
│   ├── models/
│   │   ├── job.py                # Job models
│   │   ├── dataset.py            # Dataset models
│   │   └── result.py             # Result models
│   └── workers/
│       ├── tasks.py              # Celery tasks
│       └── __init__.py
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   └── test_api.py               # API tests
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Configuration

Edit `.env` file to configure:

```env
# Server
DEBUG=False
LOG_LEVEL=INFO

# Database & Cache
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./webgenie.db

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# File Storage
DATA_DIR=/data
RESULTS_DIR=/data/results
DATASETS_DIR=/data/datasets

# Algorithms
USE_DOCKER=True
ALGORITHM_TIMEOUT=86400
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Verbose output
pytest -v
```

## 📊 Monitoring

### Flower Dashboard
Monitor Celery tasks in real-time at http://localhost:5555

### Logs
- **Docker**: `docker-compose logs -f backend`
- **Local**: Check `/var/log/webgenie/app.log`

### API Health
```bash
curl http://localhost:8000/health
```

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t webgenie-backend:latest .
```

### Run Container
```bash
docker run -d \
  -p 8000:8000 \
  -v /data:/data \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e REDIS_URL=redis://redis:6379/0 \
  webgenie-backend:latest
```

### Production Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

## 🤝 Integration with Frontend

The backend is designed to be integrated with the frontend. Configure CORS in `.env`:

```env
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## 📝 API Response Format

All responses follow a consistent format:

### Success Response
```json
{
  "id": "job-abc123",
  "status": "completed",
  "dataset_id": "dataset-xyz",
  "algorithm": "GRNBOOST2",
  ...
}
```

### Error Response
```json
{
  "detail": "Error message describing the issue"
}
```

## 🔐 Security Considerations

- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement authentication/authorization as needed
- Validate all user inputs
- Use non-root user in containers (configured in Dockerfile)
- Set appropriate file permissions

## 📈 Performance Tips

1. **Parallel Jobs**: Adjust `MAX_CONCURRENT_JOBS` in config
2. **Memory**: Set `ALGORITHM_MEMORY_LIMIT` appropriately
3. **Timeout**: Configure `JOB_TIMEOUT_SECONDS` for long-running algorithms
4. **Caching**: Implement result caching for repeated queries
5. **Database**: Use PostgreSQL instead of SQLite for production

## 🐛 Troubleshooting

### Redis Connection Error
```bash
# Ensure Redis is running
docker ps | grep redis
# or start Redis
docker-compose up -d redis
```

### Docker Socket Error
```bash
# Ensure Docker socket is accessible
ls -la /var/run/docker.sock
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
```

### Memory Issues
```bash
# Reduce concurrent jobs
MAX_CONCURRENT_JOBS=2
# or increase container memory
docker-compose down
# Edit docker-compose.yml and adjust memory
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Beeline Repository](https://github.com/Murali-group/Beeline)
- [Algorithm Papers](https://murali-group.github.io/Beeline/)

## 📄 License

This project maintains the same license as the original Beeline project.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📧 Support

For issues and questions, please refer to the main Beeline repository or open an issue in this project.
