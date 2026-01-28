"""
Job management service.
Handles job lifecycle, persistence, and monitoring.
"""

import os
import json
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.models.job import JobStatusEnum, JobResponse
from app.workers.tasks import run_inference_job

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing jobs."""

    def __init__(self):
        """Initialize job service."""
        self.jobs_dir = settings.RESULTS_DIR
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.jobs_dir / "jobs_metadata.json"
        self._load_jobs_metadata()

    def _load_jobs_metadata(self) -> None:
        """Load jobs metadata from file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    self.jobs = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load jobs metadata: {str(e)}")
                self.jobs = {}
        else:
            self.jobs = {}

    def _save_jobs_metadata(self) -> None:
        """Save jobs metadata to file."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.jobs, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save jobs metadata: {str(e)}")

    def _generate_job_id(self) -> str:
        """Generate unique job ID."""
        return f"job-{uuid.uuid4().hex[:12]}"

    def _create_job_directory(self, job_id: str) -> Path:
        """Create job-specific directory."""
        job_dir = self.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    async def submit_job(
        self,
        dataset_id: str,
        algorithm: str,
        parameters: Dict[str, Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> JobResponse:
        """Submit a new inference job."""
        try:
            job_id = self._generate_job_id()
            job_dir = self._create_job_directory(job_id)

            # Create job metadata
            job_metadata = {
                "id": job_id,
                "dataset_id": dataset_id,
                "algorithm": algorithm,
                "parameters": parameters,
                "name": name or f"{algorithm} on {dataset_id}",
                "description": description,
                "status": JobStatusEnum.SUBMITTED.value,
                "progress": 0.0,
                "started_at": None,
                "ended_at": None,
                "error_message": None,
                "celery_task_id": None,
                "result_path": str(job_dir),
                "log_file": str(job_dir / "execution.log"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Store metadata
            self.jobs[job_id] = job_metadata
            self._save_jobs_metadata()

            # Submit async task
            dataset_path = settings.DATASETS_DIR / dataset_id / "data.csv"

            task = run_inference_job.delay(
                job_id=job_id,
                dataset_id=dataset_id,
                algorithm=algorithm,
                dataset_path=str(dataset_path),
                parameters=parameters,
            )

            # Update with task ID
            self.jobs[job_id]["celery_task_id"] = task.id
            self.jobs[job_id]["status"] = JobStatusEnum.RUNNING.value
            self.jobs[job_id]["started_at"] = datetime.utcnow().isoformat()
            self._save_jobs_metadata()

            logger.info(
                f"Job submitted",
                extra={
                    "job_id": job_id,
                    "algorithm": algorithm,
                    "dataset_id": dataset_id,
                    "task_id": task.id,
                },
            )

            return JobResponse(**self.jobs[job_id])

        except Exception as e:
            logger.error(f"Failed to submit job: {str(e)}")
            raise

    async def get_job(self, job_id: str) -> Optional[JobResponse]:
        """Get job by ID."""
        if job_id not in self.jobs:
            logger.warning(f"Job not found: {job_id}")
            return None

        job_data = self.jobs[job_id]

        # Check if associated Celery task exists and update status
        if job_data.get("celery_task_id"):
            task_id = job_data["celery_task_id"]
            # Could check Celery task state here to update status
            # For now, returning stored metadata

        return JobResponse(**job_data)

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[JobStatusEnum] = None,
        dataset_id: Optional[str] = None,
        algorithm: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List jobs with optional filters."""
        all_jobs = list(self.jobs.values())

        # Apply filters
        if status:
            all_jobs = [j for j in all_jobs if j["status"] == status.value]
        if dataset_id:
            all_jobs = [j for j in all_jobs if j["dataset_id"] == dataset_id]
        if algorithm:
            all_jobs = [j for j in all_jobs if j["algorithm"] == algorithm]

        # Sort by creation date (newest first)
        all_jobs.sort(key=lambda x: x["created_at"], reverse=True)

        total = len(all_jobs)
        items = [JobResponse(**j) for j in all_jobs[skip : skip + limit]]

        return {
            "total": total,
            "items": items,
            "page": skip // limit + 1,
            "per_page": limit,
        }

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job."""
        try:
            if job_id not in self.jobs:
                logger.warning(f"Job not found: {job_id}")
                return False

            job_data = self.jobs[job_id]

            # Check if job is still running
            if job_data["status"] not in [
                JobStatusEnum.PENDING.value,
                JobStatusEnum.SUBMITTED.value,
                JobStatusEnum.RUNNING.value,
            ]:
                logger.warning(f"Cannot cancel job with status: {job_data['status']}")
                return False

            # Try to revoke Celery task
            if job_data.get("celery_task_id"):
                from celery import current_app

                current_app.control.revoke(job_data["celery_task_id"], terminate=True)

            # Update job status
            self.jobs[job_id]["status"] = JobStatusEnum.CANCELLED.value
            self.jobs[job_id]["ended_at"] = datetime.utcnow().isoformat()
            self._save_jobs_metadata()

            logger.info(f"Job cancelled: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel job: {str(e)}")
            raise

    async def get_job_logs(self, job_id: str) -> Optional[str]:
        """Get job execution logs."""
        try:
            if job_id not in self.jobs:
                logger.warning(f"Job not found: {job_id}")
                return None

            log_file = Path(self.jobs[job_id]["log_file"])

            if not log_file.exists():
                logger.warning(f"Log file not found: {log_file}")
                return None

            with open(log_file, "r") as f:
                return f.read()

        except Exception as e:
            logger.error(f"Failed to retrieve logs: {str(e)}")
            return None

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatusEnum,
        progress: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update job status."""
        try:
            if job_id not in self.jobs:
                logger.warning(f"Job not found: {job_id}")
                return False

            self.jobs[job_id]["status"] = status.value
            self.jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()

            if progress is not None:
                self.jobs[job_id]["progress"] = max(0, min(100, progress))

            if error_message:
                self.jobs[job_id]["error_message"] = error_message

            if status in [
                JobStatusEnum.COMPLETED,
                JobStatusEnum.FAILED,
                JobStatusEnum.CANCELLED,
            ]:
                self.jobs[job_id]["ended_at"] = datetime.utcnow().isoformat()

            self._save_jobs_metadata()
            return True

        except Exception as e:
            logger.error(f"Failed to update job status: {str(e)}")
            raise


# Global service instance
job_service = JobService()
