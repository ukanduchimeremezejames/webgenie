# Frontend Integration Guide

This document describes how to integrate the frontend (located in `../frontend`) with the WebGenie backend.

## Overview

The frontend is a React/Vue application that needs to communicate with the FastAPI backend. The backend provides RESTful APIs that the frontend can consume.

## Backend API Base URL

Configure the frontend to point to the backend:

```javascript
// In frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## API Client Setup

### Using Fetch API

```typescript
// api.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function apiCall(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}

export default apiCall;
```

### Using Axios

```typescript
// api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error);
    throw error;
  }
);

export default apiClient;
```

## Key API Endpoints to Integrate

### 1. Algorithms List
```typescript
// Get available algorithms
GET /algorithms

// Response
{
  algorithms: [
    { name: "GRNBOOST2", description: "...", docker_image: "..." },
    ...
  ],
  total: 14
}
```

### 2. Datasets
```typescript
// List datasets
GET /datasets?skip=0&limit=10

// Register dataset
POST /datasets/register
{
  name: "My Dataset",
  description: "...",
  source: { source_type: "local", url: "..." },
  schema: { gene_column: "...", cell_column: "...", ... }
}

// Get dataset
GET /datasets/{dataset_id}

// Preview dataset
GET /datasets/{dataset_id}/preview?num_rows=5
```

### 3. Jobs (Inference)
```typescript
// Submit job
POST /jobs
{
  dataset_id: "...",
  algorithm: "GRNBOOST2",
  parameters: { ... }
}

// List jobs
GET /jobs?skip=0&limit=10&status=running&algorithm=GRNBOOST2

// Get job status
GET /jobs/{job_id}

// Get job logs
GET /jobs/{job_id}/logs

// Cancel job
DELETE /jobs/{job_id}
```

### 4. Results
```typescript
// Get result
GET /results/job/{job_id}

// Get result summary
GET /results/job/{job_id}/summary

// Compare networks
POST /results/compare
{ job_id_1: "...", job_id_2: "..." }

// Download network
GET /results/job/{job_id}/network/download?format=json

// Export results
POST /results/job/{job_id}/export?export_format=graphml
```

## UI Components to Implement

### 1. Algorithm Selector
```typescript
// Components/AlgorithmSelector.tsx
import { useEffect, useState } from 'react';
import apiClient from '../api';

interface Algorithm {
  name: string;
  description: string;
  docker_image: string;
}

export function AlgorithmSelector() {
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  
  useEffect(() => {
    apiClient.get('/algorithms').then(data => {
      setAlgorithms(data.algorithms);
    });
  }, []);
  
  return (
    <div>
      {algorithms.map(algo => (
        <button key={algo.name}>{algo.name}</button>
      ))}
    </div>
  );
}
```

### 2. Dataset Manager
```typescript
// Components/DatasetManager.tsx
export function DatasetManager() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const loadDatasets = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/datasets');
      setDatasets(response.items);
    } finally {
      setLoading(false);
    }
  };
  
  const registerDataset = async (dataset) => {
    await apiClient.post('/datasets/register', dataset);
    loadDatasets();
  };
  
  return (
    <div>
      {/* Dataset list and registration form */}
    </div>
  );
}
```

### 3. Job Submission Form
```typescript
// Components/JobSubmission.tsx
export function JobSubmissionForm() {
  const [formData, setFormData] = useState({
    dataset_id: '',
    algorithm: '',
    parameters: {},
    name: '',
  });
  
  const submitJob = async () => {
    const response = await apiClient.post('/jobs', formData);
    console.log('Job submitted:', response);
  };
  
  return (
    <form onSubmit={submitJob}>
      {/* Form fields */}
    </form>
  );
}
```

### 4. Job Monitor
```typescript
// Components/JobMonitor.tsx
export function JobMonitor({ jobId }: { jobId: string }) {
  const [job, setJob] = useState(null);
  const [logs, setLogs] = useState('');
  
  useEffect(() => {
    const interval = setInterval(async () => {
      const jobData = await apiClient.get(`/jobs/${jobId}`);
      setJob(jobData);
      
      if (jobData.log_file) {
        const logsData = await apiClient.get(`/jobs/${jobId}/logs`);
        setLogs(logsData.logs);
      }
    }, 2000); // Poll every 2 seconds
    
    return () => clearInterval(interval);
  }, [jobId]);
  
  return (
    <div>
      <div>Status: {job?.status}</div>
      <div>Progress: {job?.progress}%</div>
      <pre>{logs}</pre>
    </div>
  );
}
```

### 5. Result Visualization
```typescript
// Components/ResultViewer.tsx
export function ResultViewer({ jobId }: { jobId: string }) {
  const [summary, setSummary] = useState(null);
  
  useEffect(() => {
    apiClient.get(`/results/job/${jobId}/summary`).then(setSummary);
  }, [jobId]);
  
  return (
    <div>
      <h3>Network Summary</h3>
      <p>Total Edges: {summary?.total_edges}</p>
      <p>Nodes: {summary?.num_nodes}</p>
      <p>Density: {summary?.density.toFixed(4)}</p>
      <p>Avg Degree: {summary?.avg_degree.toFixed(2)}</p>
    </div>
  );
}
```

## Environment Configuration

Create `.env` file in frontend directory:

```env
# Frontend
VITE_APP_NAME=WebGenie
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000

# Analytics (optional)
VITE_GOOGLE_ANALYTICS_ID=
```

## CORS Configuration

The backend is already configured for CORS. Ensure the frontend URL is in the allowed origins:

```python
# app/core/config.py
CORS_ORIGINS = [
    "http://localhost:3000",      # Frontend dev server
    "http://localhost:5173",      # Vite dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
```

## Running Both Concurrently

### Terminal 1: Backend
```bash
cd webgenie-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Celery Worker
```bash
cd webgenie-backend
source venv/bin/activate
celery -A app.core.tasks worker --loglevel=info
```

### Terminal 3: Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:5173
Backend API at http://localhost:8000/api/v1

## WebSocket Support (Optional)

For real-time updates, you can add WebSocket support:

```python
# app/api/websocket.py
from fastapi import WebSocket, APIRouter

router = APIRouter()

@router.websocket("/ws/jobs/{job_id}")
async def websocket_job_updates(websocket: WebSocket, job_id: str):
    await websocket.accept()
    try:
        while True:
            # Send job updates
            job = await job_service.get_job(job_id)
            await websocket.send_json(job.dict())
            await asyncio.sleep(1)
    except ConnectionClosed:
        pass
```

## Authentication (Optional)

Add JWT authentication if needed:

```python
# app/core/security.py
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401)
```

## Deployment

### Frontend Deployment
```bash
# Build frontend
cd frontend
npm run build

# Deploy dist/ folder to static hosting or backend
```

### Full-Stack Deployment
```bash
# Using Docker Compose
docker-compose up -d

# Access at http://your-domain
```

## Troubleshooting

### CORS Errors
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution**: Ensure frontend URL is in `CORS_ORIGINS` in `app/core/config.py`

### API Connection Refused
```
Connection refused: http://localhost:8000
```
**Solution**: Ensure backend is running and accessible at configured URL

### Job Status Not Updating
```javascript
// Increase polling interval or use WebSocket
setInterval(() => fetchJobStatus(), 3000);
```

## Best Practices

1. **Error Handling**: Always implement proper error handling in API calls
2. **Loading States**: Show loading indicators during API requests
3. **Caching**: Cache dataset and algorithm lists to reduce API calls
4. **Polling**: Use appropriate polling intervals (2-5 seconds for job status)
5. **Type Safety**: Use TypeScript for better type checking
6. **Testing**: Test API integration with mock data

## Additional Resources

- [Frontend README](../frontend/README.md)
- [Backend API Docs](../webgenie-backend/README.md)
- [FastAPI CORS Docs](https://fastapi.tiangolo.com/tutorial/cors/)
- [Axios Documentation](https://axios-http.com/)
