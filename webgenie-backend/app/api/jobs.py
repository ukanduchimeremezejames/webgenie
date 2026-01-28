"""
API endpoints for job management.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
import logging

from app.models.job import (
    JobCreate,
    JobResponse,
    JobListResponse,
    JobStatusEnum,
    JobLogResponse,
    JobCancellationResponse,
)
from app.services.jobs_service import job_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def submit_job(job: JobCreate) -> JobResponse:
    """Submit a new inference job."""
    try:
        result = await job_service.submit_job(
            dataset_id=job.dataset_id,
            algorithm=job.algorithm,
            parameters=job.parameters,
            name=job.name,
            description=job.description,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to submit job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to submit job: {str(e)}",
        )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[JobStatusEnum] = Query(None, alias="status"),
    dataset_id: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> JobListResponse:
    """List jobs with optional filters."""
    try:
        result = await job_service.list_jobs(
            skip=skip,
            limit=limit,
            status=status_filter,
            dataset_id=dataset_id,
            algorithm=algorithm,
        )
        return JobListResponse(**result)
    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to list jobs",
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    """Get job by ID."""
    try:
        job = await job_service.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get job",
        )


@router.get("/{job_id}/logs", response_model=JobLogResponse)
async def get_job_logs(job_id: str) -> JobLogResponse:
    """Get job execution logs."""
    try:
        job = await job_service.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        logs = await job_service.get_job_logs(job_id)
        if logs is None:
            logs = "No logs available"

        return JobLogResponse(
            job_id=job_id,
            logs=logs,
            timestamp=job.updated_at or job.started_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve logs",
        )


@router.delete("/{job_id}", response_model=JobCancellationResponse)
async def cancel_job(job_id: str) -> JobCancellationResponse:
    """Cancel a job."""
    try:
        success = await job_service.cancel_job(job_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel job {job_id}",
            )

        return JobCancellationResponse(
            job_id=job_id,
            cancelled=True,
            message=f"Job {job_id} cancellation requested",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel job",
        )
