# 🧬 WebGenie - Gene Regulatory Network Inference Platform

A complete, production-ready platform for Gene Regulatory Network (GRN) inference using machine learning algorithms. Built with FastAPI, React, Docker, and integrated with HuggingFace datasets and Docker Hub algorithms.

## ✨ Features

### 🔬 Core Functionality
- **12+ GRN Algorithms**: SCODE, SCNS, SINCERITIES, PIDC, GRNVBEM, GENIE3, GRNBOOST2, LEAP, JUMP3, PPCOR, GRISLI, SINGE
- **Dataset Management**: Upload, register, and preview datasets from HuggingFace Hub
- **Job Orchestration**: Asynchronous job submission and monitoring with Celery
- **Result Analysis**: Network comparison, metrics computation, multi-format export
- **Real-time Monitoring**: Celery Flower integration for task tracking

### 🚀 Technical Stack
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python 3.11 + SQLAlchemy
- **Database**: PostgreSQL 16 + Redis 7
- **Task Queue**: Celery with Redis broker
- **Containerization**: Docker & Docker Compose
- **Cloud Deployment**: Choreo support

### 🔌 Integrations
- **HuggingFace Hub**: Dataset discovery and management from `cskokgibbs/datasets`
- **Docker Hub**: Algorithm execution from `grnbeeline` registry
- **REST API**: Complete OpenAPI/Swagger documentation
- **WebSocket Ready**: Real-time updates support

## 📋 Prerequisites

- Docker & Docker Compose v1.29+
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- Git
- 8GB+ RAM
- 20GB+ disk space

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/webgenie.git
cd webgenie

# Run quick start script
chmod +x quick-start.sh
./quick-start.sh

# Or manually start
cp .env.local .env
docker-compose up -d
```

**Access the application:**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower (Task Monitor): http://localhost:5555
- PgAdmin (Database): http://localhost:5050

### Option 2: Local Development

```bash
# Backend setup
cd webgenie-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload --port 8000

# In another terminal, start Celery
celery -A app.core.tasks worker --loglevel=info

# Frontend setup
cd ../webgenie-frontend
npm install
npm run dev  # http://localhost:5173
```

## 📁 Project Structure

```
webgenie/
├── webgenie-backend/
│   ├── app/
│   │   ├── api/              # REST API endpoints
│   │   │   ├── datasets.py   # Dataset management
│   │   │   ├── algorithms.py # Algorithm discovery
│   │   │   ├── jobs.py       # Job orchestration
│   │   │   └── results.py    # Result management
│   │   ├── core/
│   │   │   ├── config.py     # Configuration management
│   │   │   ├── logging.py    # Logging setup
│   │   │   └── tasks.py      # Celery tasks
│   │   ├── models/           # SQLAlchemy models
│   │   ├── services/
│   │   │   ├── huggingface_service.py   # HF integration
│   │   │   ├── docker_hub_service.py    # Docker algorithms
│   │   │   ├── datasets_service.py      # Dataset operations
│   │   │   └── inference_service.py     # Inference logic
│   │   └── main.py           # FastAPI app
│   ├── tests/                # Backend tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic/              # Database migrations
│
├── webgenie-frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── App.tsx       # Main React component
│   │   │   ├── types.ts      # TypeScript definitions
│   │   │   └── components/   # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── services/
│   │   │   └── api.ts        # API client
│   │   ├── hooks/
│   │   │   └── useApi.ts     # API hooks
│   │   └── styles/           # CSS files
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml        # Multi-service orchestration
├── .env.local               # Local development config
├── .env.production          # Production config
├── .env.choreo              # Choreo deployment config
├── INTEGRATION_GUIDE.md     # Complete integration guide
└── Makefile                 # Convenient commands
```

## 🔗 API Endpoints

### Datasets
```
GET    /api/v1/datasets              # List datasets
GET    /api/v1/datasets/{id}         # Get dataset details
GET    /api/v1/datasets/{id}/preview # Preview dataset
POST   /api/v1/datasets/register     # Register dataset
PATCH  /api/v1/datasets/{id}         # Update dataset
DELETE /api/v1/datasets/{id}         # Delete dataset
```

### Algorithms
```
GET  /api/v1/algorithms              # List algorithms
GET  /api/v1/algorithms/{name}       # Get algorithm details
POST /api/v1/algorithms/{name}/check-image  # Check image availability
```

### Jobs
```
POST   /api/v1/jobs                  # Submit job
GET    /api/v1/jobs                  # List jobs
GET    /api/v1/jobs/{id}             # Get job details
GET    /api/v1/jobs/{id}/logs        # Get job logs
DELETE /api/v1/jobs/{id}             # Cancel job
```

### Results
```
GET    /api/v1/results               # List results
GET    /api/v1/results/{id}          # Get result details
GET    /api/v1/results/{id}/download # Download result
DELETE /api/v1/results/{id}          # Delete result
```

## 💻 Usage Examples

### Submit an Inference Job

```typescript
import { jobApi, datasetApi } from '@/services/api';

// Get available datasets
const datasets = await datasetApi.list();

// Submit job
const job = await jobApi.submit({
  name: 'GENIE3 Analysis',
  dataset_id: datasets.items[0].id,
  algorithm: 'genie3',
  parameters: {
    n_trees: 1000
  }
});

console.log(`Job submitted: ${job.id}`);

// Monitor job progress
const jobStatus = await jobApi.get(job.id);
console.log(`Status: ${jobStatus.status}`);
```

### List Available Algorithms

```bash
curl http://localhost:8000/api/v1/algorithms | jq .
```

### Download Results

```typescript
const result = await resultApi.get(resultId);
await resultApi.download(resultId, 'graphml');
```

## 📊 Monitoring

### Celery Task Monitoring
- **Flower UI**: http://localhost:5555
- View task history, execution time, and failures
- Monitor worker status and performance

### Database Management
- **PgAdmin**: http://localhost:5050
- User: admin@example.com
- Password: admin

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 80, 3000 | React application with Nginx |
| Backend | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache & message broker |
| Celery Worker | - | Background task execution |
| Celery Beat | - | Scheduled tasks |
| Flower | 5555 | Task monitoring dashboard |
| PgAdmin | 5050 | Database administration |

## 🚀 Deployment

### Local Machine
```bash
cp .env.local .env
docker-compose up -d
```

### Production
```bash
cp .env.production .env
# Update database credentials
docker-compose -f docker-compose.yml up -d
```

### Choreo Cloud Platform
1. Create Choreo account at https://platform.wso2.com/choreo
2. Follow `INTEGRATION_GUIDE.md` for detailed steps
3. Deploy with automatic CI/CD

```bash
# Configure Choreo connection
git remote add choreo <choreo-git-url>

# Deploy backend
git push choreo main

# Deploy frontend separately in Choreo console
```

## 🔧 Configuration

### Environment Variables

**Local Development** (`.env.local`)
```bash
DEBUG=True
LOG_LEVEL=DEBUG
DB_USER=webgenie
DB_PASSWORD=webgenie_secure_password
VITE_API_URL=http://localhost:8000/api/v1
```

**Production** (`.env.production`)
```bash
DEBUG=False
LOG_LEVEL=INFO
DB_PASSWORD=your_secure_password
VITE_API_URL=https://your-domain.com/api/v1
HF_TOKEN=your_huggingface_token
```

**Choreo** (`.env.choreo`)
See `.env.choreo` for cloud-specific configuration.

## 📚 Documentation

- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Complete integration and deployment guide
- **[API Swagger](http://localhost:8000/docs)** - Interactive API documentation
- **[Backend README](./webgenie-backend/README.md)** - Backend-specific documentation
- **[Frontend README](./webgenie-frontend/README.md)** - Frontend-specific documentation

## 🛠️ Development

### Using Makefile (Recommended)

```bash
# Start services
make start

# View logs
make logs

# Run tests
make test

# Build images
make build

# Check API health
make api-health

# Deploy to Choreo
make choreo-backend
```

### Manual Commands

```bash
# Start specific service
docker-compose up -d backend celery_worker

# View service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend python -m app.core.config

# Run tests
docker-compose exec backend pytest tests/

# Database operations
docker-compose exec postgres psql -U webgenie -d webgenie_db
```

## ✅ Testing

### Backend Tests
```bash
make test-backend
# or
docker-compose exec backend pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
make test-frontend
# or
cd webgenie-frontend && npm run test
```

### End-to-End Testing
```bash
# Run full test suite
make test
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

**Database Connection Error**
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Verify credentials in .env
# Reset database
docker-compose exec postgres psql -U webgenie -d webgenie_db -c "SELECT 1;"
```

**Celery Not Processing Jobs**
```bash
# Check worker logs
docker-compose logs celery_worker

# Verify Redis connection
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart celery_worker
```

**Frontend API Calls Failing**
```bash
# Check backend health
curl http://localhost:8000/health

# Verify CORS settings
# Check browser console for errors
# Ensure correct API URL in .env
```

See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md#troubleshooting) for more troubleshooting tips.

## 📊 Performance Tuning

```bash
# Scale Celery workers
docker-compose up -d --scale celery_worker=3

# Increase worker concurrency
docker-compose exec celery_worker celery -A app.core.tasks worker -c 8

# Monitor Docker resource usage
docker stats

# Optimize PostgreSQL
docker-compose exec postgres psql -U webgenie -d webgenie_db -c "ANALYZE;"
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For issues, questions, or suggestions:
- **Issues**: GitHub Issues
- **Documentation**: See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)
- **API Docs**: http://localhost:8000/docs

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [React](https://react.dev/) + [Vite](https://vitejs.dev/)
- Task queue using [Celery](https://docs.celeryproject.io/)
- Database with [PostgreSQL](https://www.postgresql.org/)
- Algorithms from [Beeline](https://beeline.readthedocs.io/)
- Datasets from [HuggingFace Hub](https://huggingface.co/)

---

**Made with ❤️ for Gene Regulatory Network Research**

Last updated: January 28, 2026
