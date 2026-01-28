# WebGenie - Quick Reference Card

## 🚀 Quick Start (Choose One)

### Option A: Automated Script (Recommended)
```bash
cd webgenie
chmod +x quick-start.sh
./quick-start.sh
```

### Option B: Docker Compose
```bash
cd webgenie
cp .env.local .env
docker-compose up -d
```

### Option C: Makefile
```bash
cd webgenie
make start
```

---

## 📍 Access URLs

| Service | URL | User/Pass |
|---------|-----|-----------|
| Frontend | http://localhost | - |
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Celery Flower | http://localhost:5555 | - |
| PgAdmin | http://localhost:5050 | admin@example.com / admin |

---

## 🔧 Essential Commands

### Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend
```

### Using Makefile
```bash
make start          # Start all services
make stop           # Stop all services
make logs           # View all logs
make test           # Run tests
make status         # Show service status
make help           # View all commands
```

### Database
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U webgenie -d webgenie_db

# Run migrations
docker-compose exec backend alembic upgrade head

# Reset database
make db-reset
```

### Testing
```bash
# All tests
make test

# Backend only
make test-backend

# Frontend only
make test-frontend
```

---

## 📊 API Examples

### List Datasets
```bash
curl http://localhost:8000/api/v1/datasets
```

### List Algorithms
```bash
curl http://localhost:8000/api/v1/algorithms | jq .
```

### Submit a Job
```bash
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Job",
    "dataset_id": "YOUR_DATASET_ID",
    "algorithm": "genie3",
    "parameters": {}
  }'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/jobs/{job_id}
```

### Get Job Logs
```bash
curl http://localhost:8000/api/v1/jobs/{job_id}/logs
```

---

## 🔍 Troubleshooting Quick Fixes

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Check if port is in use
lsof -i :8000

# Restart service
docker-compose restart backend
```

### Database connection error
```bash
# Check PostgreSQL
docker-compose logs postgres

# Check connection
docker-compose exec postgres psql -U webgenie -d webgenie_db -c "SELECT 1;"
```

### Celery worker not working
```bash
# Check worker logs
docker-compose logs celery_worker

# Verify Redis
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart celery_worker
```

### Frontend API calls failing
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Check .env file for VITE_API_URL
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | All services configuration |
| `.env.local` | Local development settings |
| `.env.production` | Production settings |
| `.env.choreo` | Choreo cloud settings |
| `INTEGRATION_GUIDE.md` | Complete integration guide |
| `webgenie-backend/app/main.py` | Backend entry point |
| `webgenie-frontend/src/app/App.tsx` | Frontend entry point |
| `Makefile` | Automation commands |

---

## 🔑 Key Configuration

### Environment Variables
```bash
# Database
DB_USER=webgenie
DB_PASSWORD=webgenie_secure_password
DB_NAME=webgenie_db

# Frontend
VITE_API_URL=http://localhost:8000/api/v1

# HuggingFace (optional)
HF_TOKEN=your_token_here
```

### Services Port Mapping
```
PostgreSQL  → 5432
Redis       → 6379
Backend     → 8000
Frontend    → 80, 3000
Flower      → 5555
PgAdmin     → 5050
```

---

## 🚀 Deployment Checklist

### Local Development
- [ ] Clone repository
- [ ] Run `./quick-start.sh`
- [ ] Verify all services are running
- [ ] Test API endpoints
- [ ] Test frontend access

### Production
- [ ] Update `.env.production` with real credentials
- [ ] Set `DEBUG=False`
- [ ] Configure secure database password
- [ ] Update CORS_ORIGINS
- [ ] Run `docker-compose -f docker-compose.yml up -d`

### Choreo Cloud
- [ ] Create Choreo account
- [ ] Push to Choreo repository
- [ ] Set environment variables in Choreo console
- [ ] Configure managed database (PostgreSQL)
- [ ] Configure managed cache (Redis)
- [ ] Deploy backend service
- [ ] Deploy frontend service
- [ ] Update frontend VITE_API_URL to Choreo backend URL

---

## 📊 Monitor Services

### Real-time Monitoring
```bash
# View all containers
docker-compose ps

# View resource usage
docker stats

# View specific service logs
docker-compose logs -f celery_worker

# Celery Flower dashboard
# Open http://localhost:5555
```

### Database Monitoring
```bash
# PgAdmin
# Open http://localhost:5050
# Email: admin@example.com
# Password: admin
```

---

## 🔗 API Endpoints Quick List

### Datasets
```
GET    /api/v1/datasets
GET    /api/v1/datasets/{id}
GET    /api/v1/datasets/{id}/preview
POST   /api/v1/datasets/register
PATCH  /api/v1/datasets/{id}
DELETE /api/v1/datasets/{id}
```

### Algorithms
```
GET  /api/v1/algorithms
GET  /api/v1/algorithms/{name}
POST /api/v1/algorithms/{name}/check-image
```

### Jobs
```
POST   /api/v1/jobs
GET    /api/v1/jobs
GET    /api/v1/jobs/{id}
GET    /api/v1/jobs/{id}/logs
DELETE /api/v1/jobs/{id}
```

### Results
```
GET    /api/v1/results
GET    /api/v1/results/{id}
GET    /api/v1/results/{id}/download
DELETE /api/v1/results/{id}
```

---

## 💡 Tips & Tricks

### Quick Health Check
```bash
curl http://localhost:8000/health
```

### View All Algorithms
```bash
curl http://localhost:8000/api/v1/algorithms | jq '.algorithms[] | {name, description}'
```

### Check Worker Status
```bash
# Open Flower dashboard
open http://localhost:5555
```

### View Real-time Logs
```bash
docker-compose logs -f --tail=50 backend
```

### Scale Celery Workers
```bash
docker-compose up -d --scale celery_worker=3
```

### Force Database Sync
```bash
docker-compose exec backend alembic stamp head
docker-compose exec backend alembic upgrade head
```

---

## 📞 Help & Documentation

- **Full Guide**: Read `INTEGRATION_GUIDE.md`
- **README**: Read `README_INTEGRATION.md`
- **API Docs**: Visit http://localhost:8000/docs
- **Swagger UI**: Visit http://localhost:8000/docs
- **ReDoc**: Visit http://localhost:8000/redoc
- **Flower**: Visit http://localhost:5555

---

## ⚡ Performance Tips

1. **Increase Celery concurrency** for faster job execution
2. **Scale workers** to handle more jobs: `docker-compose up -d --scale celery_worker=3`
3. **Use indexed queries** in database
4. **Enable Redis caching** for frequently accessed data
5. **Monitor resource usage** with `docker stats`

---

## 🔐 Security Reminders

- ✅ Change default database password in production
- ✅ Update CORS_ORIGINS for your domain
- ✅ Use HTTPS in production
- ✅ Rotate HuggingFace tokens regularly
- ✅ Keep Docker images updated
- ✅ Monitor logs for suspicious activity

---

**Everything you need to run WebGenie locally, in production, or on Choreo!**

For detailed information, see `INTEGRATION_GUIDE.md` and `README_INTEGRATION.md`.
