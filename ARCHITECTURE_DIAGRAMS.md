# WebGenie System Architecture & Data Flow Diagrams

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                    (React + Tailwind CSS)                           │
│                    Frontend (Nginx, Port 80)                        │
└────────────────────┬──────────────────────────────────────────────┘
                     │
                     │ REST API Calls (JSON)
                     │ CORS Enabled
                     │
┌────────────────────▼──────────────────────────────────────────────┐
│                      API GATEWAY                                   │
│                   (FastAPI, Port 8000)                            │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Routes:                                                     │  │
│  │  /api/v1/datasets   - Dataset Management                  │  │
│  │  /api/v1/algorithms - Algorithm Discovery                 │  │
│  │  /api/v1/jobs       - Job Orchestration                   │  │
│  │  /api/v1/results    - Result Management                   │  │
│  │  /health            - Health Check                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────┬─────────────┬──────────────────┬──────────────────┬───────────┘
     │             │                  │                  │
     │             │                  │                  │
┌────▼────┐   ┌────▼──────┐   ┌─────▼─────┐    ┌──────▼──────┐
│Database  │   │ Cache &   │   │   Task    │    │  External  │
│          │   │ Broker    │   │   Queue   │    │  Services  │
│PostgreSQL│   │           │   │           │    │            │
│  16      │   │ Redis 7   │   │  Celery   │    │ HuggingFace│
│ Port:    │   │ Port:     │   │ + Redis   │    │ Docker Hub │
│ 5432     │   │ 6379      │   │           │    │            │
└─────────┘   └──────────┘   └──────┬────┘    └────────────┘
                                    │
                         ┌──────────▼────────────┐
                         │   Celery Worker       │
                         │                       │
                         │ ┌──────────────────┐  │
                         │ │ Docker Engine    │  │
                         │ │ (Algorithms)     │  │
                         │ │                  │  │
                         │ │ Executes:        │  │
                         │ │ • SCODE          │  │
                         │ │ • GENIE3         │  │
                         │ │ • GRNBOOST2      │  │
                         │ │ • ... (12 total) │  │
                         │ └──────────────────┘  │
                         └───────────────────────┘

                         ┌──────────────────────┐
                         │ Monitoring           │
                         │ ┌──────────────────┐ │
                         │ │ Flower (5555)    │ │
                         │ │ Task Dashboard   │ │
                         │ └──────────────────┘ │
                         │ ┌──────────────────┐ │
                         │ │ PgAdmin (5050)   │ │
                         │ │ Database UI      │ │
                         │ └──────────────────┘ │
                         └──────────────────────┘
```

---

## 2. Data Flow Diagram

### A. Job Submission Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interaction                              │
│  1. User selects dataset from Dataset selector                  │
│  2. User chooses algorithm from Algorithm dropdown              │
│  3. User sets algorithm parameters                              │
│  4. User clicks "Submit Job" button                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
          ┌───────────────────┐
          │ Frontend Component│
          │  submits via      │
          │ jobApi.submit()   │
          └────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ POST /api/v1/jobs   │
        └────────┬────────────┘
                 │ JSON Payload:
                 │ {
                 │   "name": "string",
                 │   "dataset_id": "uuid",
                 │   "algorithm": "string",
                 │   "parameters": {}
                 │ }
                 ▼
        ┌────────────────────────┐
        │  Backend API Handler   │
        │  (jobs.py)             │
        │                        │
        │ 1. Validate input      │
        │ 2. Check dataset exists│
        │ 3. Check algorithm ok  │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  Create Job Record     │
        │  in Database           │
        │                        │
        │ INSERT INTO jobs:      │
        │ - id (UUID)            │
        │ - dataset_id           │
        │ - algorithm            │
        │ - status: PENDING      │
        │ - parameters           │
        │ - created_at           │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │ Submit to Celery Queue │
        │ (via Redis broker)     │
        │                        │
        │ celery_app.send_task() │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │ Return to Frontend:    │
        │ {                      │
        │   "id": "uuid",        │
        │   "status": "PENDING", │
        │   ...                  │
        │ }                      │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  Frontend Updates UI   │
        │  Shows job in list     │
        │  Starts polling for    │
        │  status updates        │
        └────────────────────────┘
```

### B. Job Execution Flow

```
┌──────────────────────────────────┐
│  Celery Worker polls Redis queue │
│  Finds new job task              │
└────────────┬─────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ Update job status  │
    │ PENDING → RUNNING  │
    │ Set started_at     │
    └────────┬───────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Fetch dataset from database│
    │ Load data files            │
    └────────┬───────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Get algorithm config       │
    │ from docker_hub_service.py │
    │                            │
    │ Example: genie3            │
    │ Image: grnbeeline/genie3   │
    │ Params: {n_trees: 1000}    │
    └────────┬───────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Pull Docker image:         │
    │ docker pull grnbeeline/... │
    │                            │
    │ (if not already available) │
    └────────┬───────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Create Docker container    │
    │                            │
    │ Mount volumes:             │
    │ /input ← dataset file      │
    │ /output ← results dir      │
    │                            │
    │ Set environment vars       │
    │ Set resource limits        │
    └────────┬───────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Execute algorithm in       │
    │ container                  │
    │                            │
    │ Runs: python -m genie3 ... │
    │ Timeout: 24 hours          │
    │ Memory: 8GB max            │
    └────────┬───────────────────┘
             │
    ┌────────┴────────┐
    │                 │
Success             Error
    │                 │
    ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Read results │  │ Log error    │
│ from output  │  │ Update job   │
│ directory    │  │ status:      │
│              │  │ FAILED       │
└──────┬───────┘  │ Set error_   │
       │          │ message      │
       ▼          └──────────────┘
┌──────────────────┐
│ Parse results    │
│ Create result    │
│ record in DB     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Update job       │
│ status:          │
│ COMPLETED        │
│ Set completed_at │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Frontend polls   │
│ detects status   │
│ change           │
│ Refreshes UI     │
│ Shows results    │
└──────────────────┘
```

---

## 3. Frontend Component Flow

```
┌──────────────────────────────────────────────────────┐
│            React Application (src/app)               │
└──────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌──────────┐   ┌─────────────┐  ┌──────────────┐
   │ Home     │   │ Datasets    │  │ Dashboard    │
   │ Page     │   │ Page        │  │ Page         │
   └──────────┘   └──────┬──────┘  └──────┬───────┘
                         │                │
        ┌────────────────┘                │
        │                                 │
        ▼                                 ▼
   ┌─────────────────────────────────────────┐
   │         useDatasets() Hook              │
   │                                         │
   │ • Fetches datasets list                │
   │ • Manages loading state                │
   │ • Handles errors                       │
   │ • Pagination support                   │
   └──────────┬──────────────────────────────┘
              │
              ▼
    ┌──────────────────────┐
    │   api.datasetApi     │
    │                      │
    │ GET /datasets        │
    │ GET /datasets/{id}   │
    │ POST /datasets/...   │
    └──────────┬───────────┘
               │
               ▼
       ┌──────────────────┐
       │  FastAPI Backend │
       └──────────────────┘
```

---

## 4. Algorithm Execution Flow

```
┌────────────────────────────────────────┐
│      Available Algorithms (12)          │
└────────────────────────────────────────┘
        │      │       │        │        
        ▼      ▼       ▼        ▼        
    ┌────┐ ┌────┐ ┌─────┐  ┌────────┐ 
    │S.. │ │GEN │ │GRN  │  │SINCERI │
    │CODE│ │IE3 │ │VBEM │  │TIES    │
    └────┘ └────┘ └─────┘  └────────┘
       │      │       │        │
       └──────┴───────┴────────┘
              │
              ▼
    ┌──────────────────────────┐
    │ Docker Container Registry │
    │    (grnbeeline on Hub)   │
    │                          │
    │ grnbeeline/scode:latest  │
    │ grnbeeline/genie3:latest │
    │ ... (12 images)          │
    └────────┬─────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Docker Container         │
    │                          │
    │ Input: Dataset CSV       │
    │ Process: Algorithm code  │
    │ Output: Network file     │
    │ Format: GraphML/CSV      │
    └────────┬─────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Result Storage           │
    │                          │
    │ Files: /data/results/    │
    │ Database: results table  │
    │ Metadata: job_id, date   │
    └──────────────────────────┘
```

---

## 5. Database Schema

```
┌─────────────────────────────────────────────────────┐
│              PostgreSQL Database                     │
│              (webgenie_db)                          │
└─────────────────────────────────────────────────────┘

┌────────────────────────┐
│      datasets          │
├────────────────────────┤
│ id (UUID) - PK         │
│ name (VARCHAR)         │
│ description (TEXT)     │
│ source (VARCHAR)       │
│ species (VARCHAR)      │
│ tissue (VARCHAR)       │
│ genes (INTEGER)        │
│ samples (INTEGER)      │
│ schema (JSONB)         │
│ created_at (TIMESTAMP) │
│ updated_at (TIMESTAMP) │
└────────────────────────┘
         │
         │ 1:N
         │
         ▼
┌────────────────────────────┐
│         jobs               │
├────────────────────────────┤
│ id (UUID) - PK             │
│ dataset_id (UUID) - FK     │
│ name (VARCHAR)             │
│ algorithm (VARCHAR)        │
│ status (VARCHAR)           │
│ parameters (JSONB)         │
│ progress (FLOAT)           │
│ celery_task_id (VARCHAR)   │
│ created_at (TIMESTAMP)     │
│ started_at (TIMESTAMP)     │
│ completed_at (TIMESTAMP)   │
│ error_message (TEXT)       │
│ logs (TEXT)                │
└────────────────────────────┘
         │
         │ 1:N
         │
         ▼
┌────────────────────────────┐
│      results               │
├────────────────────────────┤
│ id (UUID) - PK             │
│ job_id (UUID) - FK         │
│ network_file (VARCHAR)     │
│ metrics (JSONB)            │
│ format (VARCHAR)           │
│ created_at (TIMESTAMP)     │
│ updated_at (TIMESTAMP)     │
└────────────────────────────┘

┌────────────────────────────┐
│ algorithms_cache           │
├────────────────────────────┤
│ name (VARCHAR) - PK        │
│ description (TEXT)         │
│ docker_image (VARCHAR)     │
│ parameters (JSONB)         │
│ registry (VARCHAR)         │
│ last_updated (TIMESTAMP)   │
└────────────────────────────┘
```

---

## 6. API Call Sequence - Complete Job Submission

```
Frontend                Backend                Database    Celery          Docker
   │                      │                      │            │             │
   │─────Submit Job──────>│                      │            │             │
   │  POST /api/v1/jobs   │                      │            │             │
   │  { dataset, algo }   │                      │            │             │
   │                      │                      │            │             │
   │                      │─Validate Input───>   │            │             │
   │                      │                      │            │             │
   │                      │<─Validation OK────   │            │             │
   │                      │                      │            │             │
   │                      │─Create Job Record──>│            │             │
   │                      │ INSERT INTO jobs    │            │             │
   │                      │                      │            │             │
   │                      │<─Job Created────────│            │             │
   │                      │  (id, status)       │            │             │
   │                      │                      │            │             │
   │                      │─Queue Task──────────────────────>│             │
   │                      │  Send to Redis      │            │             │
   │                      │                      │            │             │
   │<─201 Created─────────│                      │            │             │
   │ { id, status }       │                      │            │             │
   │                      │                      │       Worker Pulls     │
   │                      │                      │       Task from Queue   │
   │                      │                      │            │             │
   │   (Poll via Hook)    │                      │            │─Update───> │
   │                      │<────────Update Status Update      │ Pull Image  │
   │   Poll GET /jobs/{id}│ to RUNNING          │ status      │             │
   │<─200 Job Running────>│                      │             │             │
   │ { status: RUNNING }  │<────────────────────│             │             │
   │                      │                      │             │<──Running──│
   │   (Poll continues)   │                      │             │            │
   │                      │                      │             │ Execute    │
   │   Poll every 5s      │                      │             │ Algorithm  │
   │                      │                      │             │            │
   │                      │                      │             │ Parse      │
   │                      │                      │             │ Results    │
   │                      │                      │             │            │
   │                      │<────Update Status────Update────────>            │
   │                      │ to COMPLETED        │ Complete   │
   │                      │                      │             │
   │<─200 Job Complete───>│                      │             │
   │ { status:            │                      │             │
   │   COMPLETED }        │                      │             │
   │                      │─Store Results──────>│             │
   │                      │ INSERT INTO results │             │
   │                      │                      │             │
   │   Poll Results       │<─Results Stored─────│             │
   │<─200 Results────────>│                      │             │
   │ { network_file,      │                      │             │
   │   metrics }          │                      │             │
   │                      │                      │             │
   │ Download Result      │                      │             │
   │─GET /results/{id}──> │─Read file──────────>│             │
   │/download             │                      │             │
   │                      │                      │             │
   │<─200 Binary File─────│                      │             │
   │ (GraphML/CSV)        │                      │             │
   │                      │                      │             │
```

---

## 7. Deployment Architecture

```
LOCAL MACHINE
┌─────────────────────────────────────────────┐
│  Docker Compose                             │
│  docker-compose up -d                       │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ PostgreSQL │ Redis │ Backend │...    │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  Access:                                    │
│  • http://localhost      (Frontend)        │
│  • http://localhost:8000 (API)             │
│  • http://localhost:5555 (Flower)          │
│  • http://localhost:5050 (PgAdmin)         │
└─────────────────────────────────────────────┘


CHOREO CLOUD PLATFORM
┌────────────────────────────────────────────────┐
│                Choreo Services                 │
│  ┌──────────────────────────────────────────┐ │
│  │ Backend Service   │ Frontend Service     │ │
│  │ (FastAPI)         │ (Static Website)     │ │
│  └──────────────────────────────────────────┘ │
│                  ▼                            │
│  ┌──────────────────────────────────────────┐ │
│  │ Managed Services                         │ │
│  │ • PostgreSQL Database                    │ │
│  │ • Redis Cache                            │ │
│  │ • Auto-scaling                           │ │
│  │ • Load Balancing                         │ │
│  │ • SSL/TLS Certificate                    │ │
│  │ • Monitoring & Logging                   │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  Access:                                       │
│  • https://your-domain.com      (Frontend)   │
│  • https://api.your-domain.com   (Backend)   │
└────────────────────────────────────────────────┘
```

---

## 8. Technology Stack Summary

```
┌────────────────────────────────────────────────────────┐
│                   FRONTEND LAYER                       │
├────────────────────────────────────────────────────────┤
│ • React 18                     (UI Framework)          │
│ • TypeScript                   (Type Safety)           │
│ • Vite                         (Build Tool)            │
│ • Tailwind CSS                 (Styling)               │
│ • Radix UI                     (Component Library)     │
│ • Nginx                        (Web Server)            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                   API LAYER                            │
├────────────────────────────────────────────────────────┤
│ • FastAPI                      (Python Web Framework)  │
│ • Uvicorn                      (ASGI Server)           │
│ • Pydantic                     (Data Validation)       │
│ • OpenAPI/Swagger              (API Documentation)     │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                   DATA LAYER                           │
├────────────────────────────────────────────────────────┤
│ • PostgreSQL 16                (Primary Database)      │
│ • SQLAlchemy                   (ORM)                   │
│ • Alembic                      (Migrations)            │
│ • Redis 7                      (Cache/Message Broker) │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                  TASK QUEUE LAYER                      │
├────────────────────────────────────────────────────────┤
│ • Celery                       (Task Queue)            │
│ • Celery Beat                  (Scheduler)             │
│ • Flower                       (Monitoring)            │
│ • Redis Broker                 (Message Queue)         │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│                 EXECUTION LAYER                        │
├────────────────────────────────────────────────────────┤
│ • Docker                       (Containerization)      │
│ • Docker Compose               (Orchestration)         │
│ • Celery Workers               (Task Execution)        │
│ • Docker Hub                   (Algorithm Images)      │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│              EXTERNAL INTEGRATIONS                     │
├────────────────────────────────────────────────────────┤
│ • HuggingFace Hub              (Dataset Discovery)     │
│ • Docker Hub (grnbeeline)      (Algorithm Registry)    │
│ • Choreo Platform              (Cloud Deployment)      │
└────────────────────────────────────────────────────────┘
```

---

This comprehensive visual documentation helps understand:
✅ How components interact
✅ Data flow through the system
✅ API call sequences
✅ Database relationships
✅ Deployment options
✅ Technology stack organization
