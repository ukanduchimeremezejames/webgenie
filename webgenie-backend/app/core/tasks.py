"""
Celery task configuration for asynchronous job execution.
"""

from celery import Celery
from celery.utils.log import get_task_logger
from kombu import Exchange, Queue
from datetime import timedelta

from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    settings.PROJECT_NAME.lower().replace(" ", "-"),
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    # Task configuration
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution
    task_track_started=True,
    task_time_limit=settings.JOB_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.JOB_TIMEOUT_SECONDS - 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Result backend
    result_expires=86400,  # 24 hours
    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default", Exchange("tasks"), routing_key="tasks.#"),
        Queue("priority", Exchange("priority"), routing_key="priority.#"),
        Queue("inference", Exchange("inference"), routing_key="inference.#"),
    ),
    task_default_exchange="tasks",
    task_default_exchange_type="topic",
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Rate limiting
    task_default_rate_limit="100/m",
)

# Set up periodic tasks if needed
celery_app.conf.beat_schedule = {
    "cleanup-old-results": {
        "task": "app.workers.tasks.cleanup_old_results",
        "schedule": timedelta(hours=6),  # Every 6 hours
        "kwargs": {"days": 7},  # Clean results older than 7 days
    },
}

logger = get_task_logger(__name__)
