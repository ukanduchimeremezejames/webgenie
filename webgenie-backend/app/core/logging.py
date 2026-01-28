"""
Structured logging configuration with JSON output support.
"""

import logging
import logging.config
import json
from typing import Any, Dict
from datetime import datetime
from pathlib import Path
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add job_id if available in extra
        if hasattr(record, "job_id"):
            log_record["job_id"] = record.job_id
        if hasattr(record, "dataset_id"):
            log_record["dataset_id"] = record.dataset_id
        if hasattr(record, "algorithm"):
            log_record["algorithm"] = record.algorithm


def setup_logging() -> None:
    """Configure application logging."""

    # Ensure log directory exists
    log_dir = settings.LOG_FILE.parent
    log_dir.mkdir(parents=True, exist_ok=True)

    if settings.LOG_FORMAT == "json":
        formatter_class = CustomJsonFormatter
        formatter_kwargs = {"format": "%(message)s"}
    else:
        formatter_class = logging.Formatter
        formatter_kwargs = {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": formatter_class,
                **formatter_kwargs,
            },
            "detailed": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "%(funcName)s:%(lineno)d - %(message)s"
                )
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "filename": str(settings.LOG_FILE),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
            },
        },
        "loggers": {
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "celery": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
        },
    }

    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance."""
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    job_id: str = None,
    dataset_id: str = None,
    algorithm: str = None,
    **kwargs,
) -> None:
    """Log message with context information."""
    extra = {}
    if job_id:
        extra["job_id"] = job_id
    if dataset_id:
        extra["dataset_id"] = dataset_id
    if algorithm:
        extra["algorithm"] = algorithm
    extra.update(kwargs)

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)
