"""
Configuration management using Pydantic BaseSettings.
Supports environment variables and .env files.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Project Info
    PROJECT_NAME: str = "WebGenie - Beeline GRN Inference Backend"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "FastAPI backend for Gene Regulatory Network inference"

    # Server Configuration
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        env="CORS_ORIGINS",
    )
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./webgenie.db", env="DATABASE_URL"
    )

    # Redis Configuration (for Celery)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", env="REDIS_URL"
    )

    # Celery Configuration
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1", env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND"
    )

    # File Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = Field(default=Path("/data"), env="DATA_DIR")
    RESULTS_DIR: Path = Field(default=Path("/data/results"), env="RESULTS_DIR")
    DATASETS_DIR: Path = Field(default=Path("/data/datasets"), env="DATASETS_DIR")
    TEMP_DIR: Path = Field(default=Path("/tmp/webgenie"), env="TEMP_DIR")

    # Job Configuration
    MAX_CONCURRENT_JOBS: int = Field(default=4, env="MAX_CONCURRENT_JOBS")
    JOB_TIMEOUT_SECONDS: int = Field(default=86400, env="JOB_TIMEOUT_SECONDS")  # 24 hours
    POLL_INTERVAL_SECONDS: int = 5

    # API Configuration
    MAX_UPLOAD_SIZE: int = Field(
        default=1024 * 1024 * 500, env="MAX_UPLOAD_SIZE"  # 500MB
    )

    # Algorithm Configuration
    ALGORITHM_TIMEOUT: int = Field(default=86400, env="ALGORITHM_TIMEOUT")
    ALGORITHM_MEMORY_LIMIT: str = Field(default="8g", env="ALGORITHM_MEMORY_LIMIT")

    # HuggingFace Configuration
    HF_TOKEN: Optional[str] = Field(default=None, env="HF_TOKEN")
    HF_DATASET_ORG: str = "cskokgibbs"
    HF_DATASET_PREFIX: str = "datasets"

    # Docker Configuration
    DOCKER_REGISTRY: str = Field(default="grnbeeline", env="DOCKER_REGISTRY")
    USE_DOCKER: bool = Field(default=True, env="USE_DOCKER")

    # Logging Configuration
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: Path = Field(default=Path("/var/log/webgenie/app.log"))

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()

# Ensure required directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
settings.DATASETS_DIR.mkdir(parents=True, exist_ok=True)
settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
