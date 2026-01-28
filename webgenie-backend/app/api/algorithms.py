"""
API endpoints for algorithm management.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
import logging

from app.services.docker_hub_service import algorithm_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/algorithms", tags=["algorithms"])


@router.get("", response_model=dict)
async def list_algorithms():
    """List all available algorithms."""
    try:
        algorithms = await algorithm_manager.list_algorithms()
        return {
            "algorithms": algorithms,
            "total": len(algorithms),
            "registry": algorithm_manager.REGISTRY,
        }
    except Exception as e:
        logger.error(f"Failed to list algorithms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to list algorithms",
        )


@router.get("/{algorithm_name}", response_model=dict)
async def get_algorithm(algorithm_name: str):
    """Get algorithm details."""
    try:
        algorithm = await algorithm_manager.get_algorithm(algorithm_name)
        if not algorithm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Algorithm {algorithm_name} not found",
            )
        return algorithm
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get algorithm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get algorithm",
        )


@router.post("/{algorithm_name}/check-image")
async def check_algorithm_image(algorithm_name: str):
    """Check if algorithm Docker image is available."""
    try:
        available = await algorithm_manager.check_image_available(algorithm_name)
        return {
            "algorithm": algorithm_name,
            "image_available": available,
            "docker_image": (await algorithm_manager.get_algorithm(algorithm_name) or {}).get("docker_image"),
        }
    except Exception as e:
        logger.error(f"Failed to check algorithm image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to check algorithm image",
        )
