# Deploying WebGenie to Choreo

Choreo is a cloud platform for deploying containerized applications. This guide covers deploying both the frontend and backend components.

## Architecture Overview

Your application has these components:
- **Frontend**: React/TypeScript app served by Nginx (port 80)
- **Backend API**: FastAPI service (port 8000)
- **Database**: PostgreSQL
- **Cache/Message Broker**: Redis
- **Task Queue**: Celery workers
- **Monitoring**: Flower dashboard

## Step 1: Prerequisites

1. **Choreo Account**: Sign up at [https://choreo.dev](https://choreo.dev)
2. **Docker Images**: Both frontend and backend are containerized
3. **Git Repository**: Push code to GitHub (required for Choreo)
4. **Environment Variables**: Prepare configuration for cloud deployment

## Step 2: Prepare Your Repository Structure

Choreo works best with a specific directory structure. Create:

```
webgenie/
├── services/
│   ├── backend/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── .choreo/
│   │       └── config.yaml
│   └── frontend/
│       ├── src/
│       ├── Dockerfile
│       ├── package.json
│       └── .choreo/
│           └── config.yaml
├── docker-compose.yml
└── .github/
    └── workflows/
        └── deploy.yml
```

## Step 3: Create Choreo Configuration Files

### Backend Configuration
Create `.choreo/config.yaml` in the backend directory:

```yaml
# Backend Choreo Configuration
specVersion: 1.0.0
metadata:
  name: webgenie-backend
  description: FastAPI backend for WebGenie
  version: 1.0.0

service:
  containerConfig:
    image: webgenie-backend
    port: 8000
    env:
      - name: LOG_LEVEL
        value: INFO
      - name: DATABASE_URL
        valueFrom: 
          secretRef: DATABASE_URL
      - name: REDIS_URL
        valueFrom:
          secretRef: REDIS_URL
      - name: CELERY_BROKER_URL
        valueFrom:
          secretRef: CELERY_BROKER_URL
      - name: HF_TOKEN
        valueFrom:
          secretRef: HF_TOKEN
    resources:
      requests:
        memory: 2Gi
        cpu: 1000m
      limits:
        memory: 4Gi
        cpu: 2000m
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
```

### Frontend Configuration
Create `.choreo/config.yaml` in the frontend directory:

```yaml
# Frontend Choreo Configuration
specVersion: 1.0.0
metadata:
  name: webgenie-frontend
  description: React frontend for WebGenie
  version: 1.0.0

service:
  containerConfig:
    image: webgenie-frontend
    port: 80
    env:
      - name: VITE_API_URL
        value: https://webgenie-backend-prod.choreo.run
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 500m
```

## Step 4: Set Up Managed Services in Choreo

Choreo provides managed versions of common services. Configure these through the Choreo dashboard:

### Option A: Use Choreo's Managed Services
1. **PostgreSQL**: Use Choreo's managed PostgreSQL addon
   - Store connection string as secret: `DATABASE_URL`

2. **Redis**: Use Choreo's managed Redis addon
   - Store URLs as secrets:
     - `REDIS_URL`: redis://hostname:6379/0
     - `CELERY_BROKER_URL`: redis://hostname:6379/1
     - `CELERY_RESULT_BACKEND`: redis://hostname:6379/2

### Option B: Use External Services
- Use cloud providers like AWS RDS for PostgreSQL
- Use AWS ElastiCache or similar for Redis
- Store connection strings in Choreo secrets

## Step 5: Deploy Backend to Choreo

### Via Choreo Dashboard:

1. Log in to [Choreo Console](https://console.choreo.dev)
2. Create new project: `WebGenie`
3. Create new component: 
   - Name: `backend`
   - Type: `Service`
   - Repository: Your GitHub repo
   - Dockerfile Path: `webgenie-backend/Dockerfile`
   - Port: `8000`

4. Configure Environment Variables:
   - Add all secrets in Choreo's secret management
   - Reference them as shown in config.yaml

5. Deploy: Click "Deploy" button

### Via Choreo CLI (Alternative):

```bash
# Install Choreo CLI
# Follow: https://github.com/wso2/choreo-cli

# Login
choreo login

# Create project
choreo project create -n WebGenie

# Deploy backend
choreo service deploy \
  --name backend \
  --dockerfile webgenie-backend/Dockerfile \
  --port 8000 \
  --project WebGenie
```

## Step 6: Deploy Frontend to Choreo

### Via Choreo Dashboard:

1. Create new component:
   - Name: `frontend`
   - Type: `Service`
   - Repository: Your GitHub repo
   - Dockerfile Path: `webgenie-frontend/Dockerfile`
   - Port: `80`

2. Configure:
   - Environment Variables: Set `VITE_API_URL` to your backend's Choreo URL
   - Example: `https://webgenie-backend-<org>-prod.choreo.run`

3. Deploy

## Step 7: Configure CORS and Networking

Update backend's CORS settings to allow your frontend URL:

### In `webgenie-backend/app/core/config.py`:

```python
from typing import List

class Settings:
    # ... existing settings ...
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://webgenie-frontend-<org>-prod.choreo.run",
        # Add your actual Choreo frontend URL
    ]
```

## Step 8: Set Up Environment Secrets

In Choreo Dashboard > Project Settings > Secrets, add:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://user:password@host:6379/0
CELERY_BROKER_URL=redis://user:password@host:6379/1
CELERY_RESULT_BACKEND=redis://user:password@host:6379/2
HF_TOKEN=your_huggingface_token
```

## Step 9: Deploy Additional Services (Optional)

### Celery Worker
Create separate component for background jobs:

```yaml
specVersion: 1.0.0
metadata:
  name: webgenie-celery-worker
  
service:
  containerConfig:
    image: webgenie-backend  # Same image as backend
    command: ["celery", "-A", "app.workers.tasks", "worker", "--loglevel=info"]
    env:
      - name: CELERY_BROKER_URL
        valueFrom:
          secretRef: CELERY_BROKER_URL
```

### Flower Monitoring (Optional)
For task monitoring:

```yaml
specVersion: 1.0.0
metadata:
  name: webgenie-flower
  
service:
  containerConfig:
    image: webgenie-backend
    port: 5555
    command: ["celery", "-A", "app.workers.tasks", "flower", "--port=5555"]
```

## Step 10: Verify Deployment

1. **Check Backend Health**:
   ```bash
   curl https://webgenie-backend-<org>-prod.choreo.run/health
   ```

2. **Check Frontend**:
   - Visit `https://webgenie-frontend-<org>-prod.choreo.run`

3. **View Logs**:
   - Choreo Dashboard > Component > Logs
   - Or use CLI: `choreo logs <component-id>`

4. **Monitor Metrics**:
   - Choreo Dashboard shows CPU, memory, request rates
   - Set up alerts if needed

## Step 11: Set Up CI/CD Pipeline

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Choreo

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy Backend
        run: |
          # Install Choreo CLI
          # Deploy using CLI or webhooks
          
      - name: Deploy Frontend
        run: |
          # Similar deployment steps
```

## Step 12: Database Migrations

Run database migrations in Choreo:

```bash
# Via SSH/Remote Execution
choreo exec <backend-component-id> -- python -m alembic upgrade head

# Or add to startup command in Dockerfile
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

## Troubleshooting

### Common Issues:

1. **Connection to Database Failed**
   - Check DATABASE_URL secret is set
   - Verify database service is running
   - Check network policies/firewall

2. **Frontend can't reach Backend**
   - Verify VITE_API_URL environment variable
   - Check CORS configuration
   - Ensure backend is publicly accessible

3. **Out of Memory**
   - Increase resource limits in config.yaml
   - Check for memory leaks in logs
   - Optimize query performance

4. **Build Failures**
   - Check Dockerfile paths are correct
   - Verify requirements.txt/package.json are present
   - Review build logs in dashboard

## URLs After Deployment

Your services will be accessible at:
- **Frontend**: `https://webgenie-frontend-<org>-prod.choreo.run`
- **Backend API**: `https://webgenie-backend-<org>-prod.choreo.run`
- **API Docs**: `https://webgenie-backend-<org>-prod.choreo.run/docs`

## Cost Optimization

- Use Choreo's free tier for development
- Scale down non-production environments
- Use auto-scaling policies for backend
- Monitor and set budget alerts

## Additional Resources

- [Choreo Documentation](https://wso2.com/choreo/docs/)
- [Choreo CLI Guide](https://github.com/wso2/choreo-cli)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)

## Next Steps

1. Sign up for Choreo account
2. Create organization/project
3. Set up managed services (DB, Cache)
4. Configure secrets
5. Deploy backend first
6. Deploy frontend
7. Test connectivity
8. Monitor and optimize
