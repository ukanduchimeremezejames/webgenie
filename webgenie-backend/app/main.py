"""
FastAPI main application.
Initializes app, routers, middleware, and startup events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api import datasets, jobs, results, algorithms

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")

    # Verify directories
    logger.info(f"Data directory: {settings.DATA_DIR}")
    logger.info(f"Results directory: {settings.RESULTS_DIR}")
    logger.info(f"Datasets directory: {settings.DATASETS_DIR}")
    logger.info(f"Temp directory: {settings.TEMP_DIR}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Custom exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(
    datasets.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    jobs.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    results.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    algorithms.router,
    prefix=settings.API_V1_PREFIX,
)


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
        "debug": settings.DEBUG,
    }


# Root endpoint
@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "api_prefix": settings.API_V1_PREFIX,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": "/health",
    }


@app.get(f"{settings.API_V1_PREFIX}/algorithms")
async def get_algorithms() -> dict:
    """Get list of available algorithms."""
    algorithms = [
        {
            "name": "SCODE",
            "description": "Single-Cell Optimal Experiment Design",
            "docker_image": f"{settings.DOCKER_REGISTRY}/scode",
        },
        {
            "name": "SCNS",
            "description": "Single-Cell Network Synthesis",
            "docker_image": f"{settings.DOCKER_REGISTRY}/scns",
        },
        {
            "name": "SINCERITIES",
            "description": "Simultaneous Circuit Inference and Clustering",
            "docker_image": f"{settings.DOCKER_REGISTRY}/sincerities",
        },
        {
            "name": "PIDC",
            "description": "Partial Information Decomposition and Context",
            "docker_image": f"{settings.DOCKER_REGISTRY}/pidc",
        },
        {
            "name": "GRNVBEM",
            "description": "Gene Regulatory Network Variational Bayes EM",
            "docker_image": f"{settings.DOCKER_REGISTRY}/grnvbem",
        },
        {
            "name": "GENIE3",
            "description": "GRN Inference using Ensemble trees",
            "docker_image": f"{settings.DOCKER_REGISTRY}/genie3",
        },
        {
            "name": "GRNBOOST2",
            "description": "GRN inference using Gradient Boosting",
            "docker_image": f"{settings.DOCKER_REGISTRY}/grnboost2",
        },
        {
            "name": "LEAP",
            "description": "Laplacian Eigenmaps",
            "docker_image": f"{settings.DOCKER_REGISTRY}/leap",
        },
        {
            "name": "JUMP3",
            "description": "Jump3: Gene Regulatory Network Inference from Multi-Platform Data",
            "docker_image": f"{settings.DOCKER_REGISTRY}/jump3",
        },
        {
            "name": "PPCOR",
            "description": "Partial Pearson Correlation",
            "docker_image": f"{settings.DOCKER_REGISTRY}/ppcor",
        },
        {
            "name": "GRISLI",
            "description": "Gene Regulatory Inference from Single-cell Lineages",
            "docker_image": f"{settings.DOCKER_REGISTRY}/grisli",
        },
        {
            "name": "SINGE",
            "description": "Single-cell Inference of Networks using Granger Ensembles",
            "docker_image": f"{settings.DOCKER_REGISTRY}/singe",
        },
        {
            "name": "SCRIBE",
            "description": "Single-Cell Regulation through Iterative Back-Edges",
            "docker_image": f"{settings.DOCKER_REGISTRY}/scribe",
        },
        {
            "name": "SCSGL",
            "description": "Single-Cell Sparse Graphical Lasso",
            "docker_image": f"{settings.DOCKER_REGISTRY}/scsgl",
        },
    ]
    return {
        "algorithms": algorithms,
        "total": len(algorithms),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
