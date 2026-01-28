# WebGenie - Complete Integration & Deployment Guide

## Table of Contents
1. [Quick Start - Local Development](#quick-start)
2. [Architecture Overview](#architecture)
3. [API Integration](#api-integration)
4. [Docker Compose Setup](#docker-compose)
5. [Deployment to Choreo](#choreo-deployment)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start - Local Development {#quick-start}

### Prerequisites
- Docker & Docker Compose (v1.29+)
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

### Step 1: Clone and Setup

```bash
cd webgenie
cp .env.local .env
```

### Step 2: Start All Services

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or individual services
docker-compose up -d postgres redis backend
docker-compose up -d celery_worker celery_beat flower frontend
```

### Step 3: Access the Application

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost | Web UI |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger Documentation |
| Celery Flower | http://localhost:5555 | Task Monitoring |
| PgAdmin | http://localhost:5050 | Database Management |

### Step 4: Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# List available algorithms
curl http://localhost:8000/api/v1/algorithms

# List datasets
curl http://localhost:8000/api/v1/datasets
```

---

## Architecture Overview {#architecture}

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)              │
│                   (Nginx - Port 80/3000)                │
└────────────────────────┬────────────────────────────────┘
                         │ REST API Calls
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI - Port 8000)              │
│  ┌─────────────────────────────────────────────────┐    │
│  │ API Routes:                                     │    │
│  │ • /api/v1/datasets - Dataset Management         │    │
│  │ • /api/v1/algorithms - Algorithm Discovery      │    │
│  │ • /api/v1/jobs - Job Submission & Monitoring    │    │
│  │ • /api/v1/results - Result Management           │    │
│  └─────────────────────────────────────────────────┘    │
└────────┬────────────────┬────────────────┬───────────────┘
         │                │                │
    ┌────▼─┐      ┌──────▼──────┐    ┌─────▼─────┐
    │      │      │             │    │           │
┌──▼──┐ ┌─▼──┐ ┌─▼────┐   ┌────▼─┐ │           │
│ DB  │ │Redis│ │Celery│   │Docker│ │ External │
│     │ │Cache│ │Queue │   │Engine│ │ Services │
│ Pg  │ │     │ │      │   │      │ │(HF, DH) │
└─────┘ └────┘ └──────┘   └──────┘ └───────────┘
```

### Data Flow

```
1. Frontend submits job request
   ↓
2. Backend validates and stores in PostgreSQL
   ↓
3. Job pushed to Celery/Redis queue
   ↓
4. Celery worker pulls job from queue
   ↓
5. Algorithm Docker image pulled from Docker Hub
   ↓
6. Algorithm executed in isolated container
   ↓
7. Results stored and job status updated
   ↓
8. Frontend polls for updates (via Flower/Celery API)
   ↓
9. Results displayed in UI
```

---

## API Integration {#api-integration}

### Frontend API Client Setup

The frontend has a pre-configured API client in `src/services/api.ts`:

```typescript
// Example usage in React components
import { useDatasets, useSubmitJob } from '@/hooks/useApi';

export function DatasetSelector() {
  const { data, loading, error } = useDatasets();
  const { submit: submitJob } = useSubmitJob();

  const handleRunAlgorithm = async (datasetId: string, algorithm: string) => {
    try {
      const job = await submitJob({
        name: `${algorithm} on ${datasetId}`,
        dataset_id: datasetId,
        algorithm: algorithm,
        parameters: {}
      });
      console.log('Job submitted:', job.id);
    } catch (err) {
      console.error('Failed to submit job:', err);
    }
  };

  // Component JSX...
}
```

### Backend API Endpoints

#### Datasets

```bash
# List datasets
GET /api/v1/datasets?skip=0&limit=10

# Get specific dataset
GET /api/v1/datasets/{dataset_id}

# Get dataset preview
GET /api/v1/datasets/{dataset_id}/preview?num_rows=5

# Register new dataset
POST /api/v1/datasets/register
Content-Type: application/json
{
  "name": "My Dataset",
  "description": "Description",
  "source": "huggingface://cskokgibbs/datasets",
  "species": "human",
  "tissue": "blood"
}

# Update dataset
PATCH /api/v1/datasets/{dataset_id}

# Delete dataset
DELETE /api/v1/datasets/{dataset_id}
```

#### Algorithms

```bash
# List all algorithms
GET /api/v1/algorithms

# Get algorithm details
GET /api/v1/algorithms/{algorithm_name}

# Check if Docker image is available
POST /api/v1/algorithms/{algorithm_name}/check-image
```

Available algorithms:
- `scode` - Single-Cell Optimal Experiment Design
- `scns` - Single-Cell Network Synthesis
- `sincerities` - Simultaneous Circuit Inference
- `pidc` - Partial Information Decomposition
- `grnvbem` - Gene Regulatory Network VB-EM
- `genie3` - Ensemble Regression Trees
- `grnboost2` - Gradient Boosting
- `leap` - Linear Equation Assumption
- `jump3` - Jump3 Inference
- `ppcor` - Partial Pearson Correlation
- `grisli` - Sparse Linear Model
- `singe` - Sparse Inverse Covariance

#### Jobs

```bash
# Submit new job
POST /api/v1/jobs
Content-Type: application/json
{
  "name": "Job Name",
  "dataset_id": "dataset-uuid",
  "algorithm": "genie3",
  "parameters": {
    "n_trees": 1000
  }
}

# List jobs
GET /api/v1/jobs?skip=0&limit=10&status=RUNNING&dataset_id=xxx

# Get job details
GET /api/v1/jobs/{job_id}

# Get job logs
GET /api/v1/jobs/{job_id}/logs

# Cancel job
DELETE /api/v1/jobs/{job_id}
```

#### Results

```bash
# List results
GET /api/v1/results?skip=0&limit=10

# Get result details
GET /api/v1/results/{result_id}

# Download result
GET /api/v1/results/{result_id}/download?format=graphml

# Delete result
DELETE /api/v1/results/{result_id}
```

---

## Docker Compose Setup {#docker-compose}

### Service Configuration

**PostgreSQL** (postgres)
- Port: 5432
- Database: webgenie_db
- User: webgenie
- Volume: postgres_data

**Redis** (redis)
- Port: 6379
- Purpose: Caching and Celery message broker

**Backend** (backend)
- Port: 8000
- Framework: FastAPI
- Depends on: PostgreSQL, Redis

**Celery Worker** (celery_worker)
- Purpose: Execute inference jobs
- Concurrency: 4 workers
- Docker-in-Docker: Enabled for algorithm execution

**Celery Beat** (celery_beat)
- Purpose: Scheduled task execution

**Flower** (flower)
- Port: 5555
- Purpose: Monitor Celery tasks

**Frontend** (frontend)
- Port: 80, 3000
- Framework: React + Vite
- Server: Nginx

**PgAdmin** (pgadmin)
- Port: 5050
- Purpose: Database administration UI

### Managing Services

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend

# Restart specific service
docker-compose restart backend

# Scale workers
docker-compose up -d --scale celery_worker=3

# Remove all containers and data
docker-compose down -v

# Execute command in container
docker-compose exec backend python -m app.core.config
```

---

## Deployment to Choreo {#choreo-deployment}

### Choreo Platform Setup

1. **Create Choreo Account**
   - Visit https://platform.wso2.com/choreo
   - Sign up and create a new project

2. **Create Backend Service**
   - Service Type: REST API
   - Source: Connect your GitHub repository
   - Build Pack: Python
   - Port: 8000
   - Environment Variables (add from .env.choreo)

3. **Create Frontend Service**
   - Service Type: Static Website
   - Build Command: `npm run build`
   - Publish Path: `dist`

### Environment Setup for Choreo

Create `.env.choreo` with:

```bash
# Server
DEBUG=False
LOG_LEVEL=INFO

# Database
DB_USER=webgenie_choreo
DB_PASSWORD=${CHOREO_DB_PASSWORD}
DB_HOST=${CHOREO_DB_HOST}
DB_PORT=5432
DB_NAME=webgenie_choreo_db

# External Services
REDIS_URL=redis://${CHOREO_REDIS_HOST}:6379/0
CELERY_BROKER_URL=redis://${CHOREO_REDIS_HOST}:6379/1
CELERY_RESULT_BACKEND=redis://${CHOREO_REDIS_HOST}:6379/2

# API Configuration
VITE_API_URL=${CHOREO_BACKEND_URL}/api/v1
CORS_ORIGINS=${CHOREO_FRONTEND_URL},${CHOREO_BACKEND_URL}

# External APIs
HF_TOKEN=${CHOREO_HF_TOKEN}
```

### Deployment Steps

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial WebGenie integration with Docker Compose"
git push origin main
```

2. **Deploy Backend**
- Create new service in Choreo
- Select "FastAPI/Python" template
- Point to `webgenie-backend` directory
- Add environment variables
- Deploy

3. **Deploy Frontend**
- Create new service in Choreo
- Select "Vite" or "Node.js" template
- Point to `webgenie-frontend` directory
- Set build command: `npm install && npm run build`
- Deploy

4. **Configure Database**
- Use Choreo's managed PostgreSQL or create external RDS
- Update DB_HOST, DB_USER, DB_PASSWORD in environment

5. **Configure Redis**
- Use Choreo's managed Redis or create external instance
- Update REDIS_URL, CELERY_BROKER_URL in environment

### Production Considerations

- Enable HTTPS/TLS
- Configure custom domain
- Set up monitoring and logging
- Enable auto-scaling
- Configure backup policies
- Set resource limits

### Monitoring Deployed Services

```bash
# View Choreo console logs
# View deployment status
# Monitor API health
# Check service uptime
# Review error rates
```

---

## Troubleshooting {#troubleshooting}

### Common Issues

#### 1. Docker Daemon Connection Error
```bash
# Solution: Ensure Docker is running
docker ps

# On Windows, use Docker Desktop
# On Linux, start Docker daemon:
sudo systemctl start docker
```

#### 2. Port Already in Use
```bash
# Find and kill process on port
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

#### 3. Database Connection Error
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Verify credentials in .env file
# Ensure database is initialized
docker-compose exec postgres psql -U webgenie -d webgenie_db -c "\dt"
```

#### 4. Celery Worker Not Processing Jobs
```bash
# Check worker logs
docker-compose logs celery_worker

# Verify Redis connection
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart celery_worker
```

#### 5. Frontend API Calls Failing
```bash
# Check API URL in frontend config
# Verify CORS settings in backend
# Check browser console for errors
# Ensure backend is running: curl http://localhost:8000/health
```

#### 6. Algorithm Docker Image Not Found
```bash
# Pull image manually
docker pull grnbeeline/genie3:latest

# Check available images
docker images | grep grnbeeline

# Verify DOCKER_REGISTRY setting in environment
```

### Debugging Techniques

```bash
# Check all container status
docker-compose ps

# View environment variables in container
docker-compose exec backend env

# Run database query
docker-compose exec postgres psql -U webgenie -d webgenie_db -c "SELECT * FROM jobs;"

# Monitor Docker resource usage
docker stats

# Inspect network
docker network inspect webgenie_webgenie-network
```

### Performance Optimization

```bash
# Increase Celery concurrency
CONCURRENCY=8 docker-compose up celery_worker

# Scale multiple workers
docker-compose up -d --scale celery_worker=3

# Optimize PostgreSQL
docker-compose exec postgres psql -U webgenie -d webgenie_db -c "ANALYZE;"

# Monitor API response times
curl -w "@curl-format.txt" http://localhost:8000/api/v1/datasets
```

---

## Support & Documentation

- **Backend API Docs**: http://localhost:8000/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Celery Docs**: https://docs.celeryproject.io/
- **Docker Docs**: https://docs.docker.com/
- **React Docs**: https://react.dev/
- **Choreo Docs**: https://platform.wso2.com/choreo/docs

---

## Next Steps

1. ✅ Set up local development environment
2. ✅ Integrate HuggingFace datasets
3. ✅ Pull Docker Hub algorithms
4. ✅ Test job submission and execution
5. ✅ Deploy to Choreo
6. ✅ Configure monitoring and alerting
7. ✅ Set up continuous deployment
