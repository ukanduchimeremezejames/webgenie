# Quick Start Guide for Choreo Deployment

## Prerequisites

1. **Choreo Account**: Sign up at https://choreo.dev (free tier available)
2. **GitHub Account**: Push your code to GitHub
3. **Docker**: For local testing before cloud deployment
4. **Choreo CLI** (optional): For CLI-based deployment

## Quick Start - 5 Steps to Deploy

### Step 1: Prepare Your Code

Make sure your GitHub repository contains:
- `webgenie-backend/` with Dockerfile
- `webgenie-frontend/` with Dockerfile
- `.choreo/` configuration files (already created)

### Step 2: Create Choreo Organization

1. Go to https://console.choreo.dev
2. Sign up with GitHub account
3. Create organization (e.g., "webgenie-org")
4. Create project (e.g., "webgenie-prod")

### Step 3: Set Up Managed Services

**Database:**
1. In Choreo dashboard, go to "Add-ons" or "Managed Services"
2. Select PostgreSQL
3. Create instance with name: `webgenie-db`
4. Copy connection string and save as secret `DATABASE_URL`

**Cache/Message Broker:**
1. Add Redis add-on
2. Create instance with name: `webgenie-redis`
3. Copy Redis URL and save as these secrets:
   - `REDIS_URL`: redis://host:6379/0
   - `CELERY_BROKER_URL`: redis://host:6379/1
   - `CELERY_RESULT_BACKEND`: redis://host:6379/2

### Step 4: Deploy Backend

1. In Choreo console, click "Create Component"
2. Select "Service" (or "API" for REST services)
3. Configure:
   - **Name**: webgenie-backend
   - **Description**: FastAPI backend
   - **GitHub Repo**: Select your repo
   - **Dockerfile Path**: webgenie-backend/Dockerfile
   - **Port**: 8000
   - **Branch**: main

4. Add Environment Variables:
   - Click "Configs & Secrets" tab
   - Add all secrets from Step 3
   - Add HF_TOKEN if using HuggingFace models

5. Click "Deploy" - wait for build to complete

6. Once deployed, copy the service URL (e.g., `https://webgenie-backend-<org>-prod.choreo.run`)

### Step 5: Deploy Frontend

1. Create another component with:
   - **Name**: webgenie-frontend
   - **Dockerfile Path**: webgenie-frontend/Dockerfile
   - **Port**: 80

2. Add Environment Variable:
   - **Name**: VITE_API_URL
   - **Value**: https://webgenie-backend-<org>-prod.choreo.run (from Step 4)

3. Click "Deploy"

4. Once deployed, access at the provided URL (e.g., `https://webgenie-frontend-<org>-prod.choreo.run`)

## Troubleshooting

### Backend won't start
```bash
# Check logs in Choreo dashboard:
# Dashboard > Component > Logs tab
# Look for database connection errors
```

If DATABASE_URL is wrong:
- Update the secret in Choreo dashboard
- Restart the component (redeploy or restart button)

### Frontend shows "Cannot reach API"
- Verify VITE_API_URL is correctly set
- Check backend is running and accessible
- Ensure CORS is enabled in backend
- Update backend's CORS_ORIGINS secret if needed

### Deployment takes too long
- Normal build time: 3-5 minutes
- If stuck longer, check logs for build errors
- Try rebuilding or redeploying

## What's Deployed Where

| Service | Choreo URL | Purpose |
|---------|-----------|---------|
| Frontend | https://webgenie-frontend-{org}-prod.choreo.run | User interface |
| Backend | https://webgenie-backend-{org}-prod.choreo.run | API server |
| API Docs | https://webgenie-backend-{org}-prod.choreo.run/docs | Swagger documentation |
| PostgreSQL | Managed by Choreo | Database |
| Redis | Managed by Choreo | Cache & message broker |

## Environment Variables Reference

### Backend Secrets (in Choreo dashboard):
```
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/1
CELERY_RESULT_BACKEND=redis://host:6379/2
HF_TOKEN=your_huggingface_token (optional)
```

### Frontend Env Vars (in Choreo dashboard):
```
VITE_API_URL=https://webgenie-backend-{org}-prod.choreo.run
```

## Testing After Deployment

1. **Test Frontend**: Open the frontend URL in browser
2. **Test Backend API**: 
   ```bash
   curl https://webgenie-backend-{org}-prod.choreo.run/health
   ```
3. **View API Docs**: Go to backend URL + `/docs`
4. **Check Backend Logs**: Choreo dashboard > Component > Logs

## Next Steps

### Optional: Set up CI/CD Pipeline
Create GitHub Actions workflow to auto-deploy on push to main:

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
      - name: Deploy
        run: |
          # Use Choreo CLI or webhooks to trigger deployment
```

### Optional: Add Custom Domain
In Choreo dashboard > Settings > Custom Domain

### Optional: Set up Monitoring
- Enable Choreo's built-in monitoring
- Set up alerts for CPU/memory/errors
- View metrics in Choreo dashboard

## Support

- Choreo Docs: https://wso2.com/choreo/docs/
- Community: https://discord.gg/choreo
- Issues: GitHub Issues tab

---

**You're now running WebGenie in the cloud!** 🚀
