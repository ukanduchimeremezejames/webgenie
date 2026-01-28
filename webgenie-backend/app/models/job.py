"""
Pydantic models for Job management.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class JobStatusEnum(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    SUBMITTED = "submitted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class JobBase(BaseModel):
    """Base job model."""

    dataset_id: str = Field(..., description="Dataset identifier")
    algorithm: str = Field(..., description="Algorithm name")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Algorithm parameters")
    name: Optional[str] = Field(default=None, description="Human-readable job name")
    description: Optional[str] = Field(default=None, description="Job description")


class JobCreate(JobBase):
    """Model for creating a job."""

    pass


class JobUpdate(BaseModel):
    """Model for updating a job."""

    status: Optional[JobStatusEnum] = None
    progress: Optional[float] = None
    error_message: Optional[str] = None


class JobResponse(JobBase):
    """Model for job response."""

    id: str = Field(..., description="Job unique identifier")
    status: JobStatusEnum = Field(..., description="Current job status")
    progress: float = Field(default=0.0, description="Progress percentage (0-100)")
    started_at: Optional[datetime] = Field(default=None, description="Job start timestamp")
    ended_at: Optional[datetime] = Field(default=None, description="Job end timestamp")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    celery_task_id: Optional[str] = Field(default=None, description="Celery task ID")
    result_path: Optional[str] = Field(default=None, description="Path to result files")
    log_file: Optional[str] = Field(default=None, description="Path to log file")

    class Config:
        """Model config."""

        from_attributes = True


class JobListResponse(BaseModel):
    """Model for job list response."""

    total: int = Field(..., description="Total number of jobs")
    items: List[JobResponse] = Field(..., description="Job list")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")


class JobLogResponse(BaseModel):
    """Model for job logs response."""

    job_id: str = Field(..., description="Job ID")
    logs: str = Field(..., description="Log content")
    timestamp: datetime = Field(..., description="Log timestamp")


class JobCancellationResponse(BaseModel):
    """Model for job cancellation response."""

    job_id: str = Field(..., description="Job ID")
    cancelled: bool = Field(..., description="Whether cancellation was successful")
    message: str = Field(..., description="Cancellation message")
