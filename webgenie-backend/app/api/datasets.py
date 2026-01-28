"""
API endpoints for dataset management.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import FileResponse
import logging

from app.models.dataset import (
    DatasetCreate,
    DatasetResponse,
    DatasetListResponse,
    DatasetPreview,
    DatasetUpdate,
)
from app.services.datasets_service import dataset_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/register", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def register_dataset(dataset: DatasetCreate) -> DatasetResponse:
    """Register a new dataset."""
    try:
        result = await dataset_service.register_dataset(
            name=dataset.name,
            description=dataset.description,
            source=dataset.source,
            schema=dataset.schema,
            species=dataset.species,
            tissue=dataset.tissue,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to register dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to register dataset: {str(e)}",
        )


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> DatasetListResponse:
    """List all registered datasets."""
    try:
        result = await dataset_service.list_datasets(skip=skip, limit=limit)
        return DatasetListResponse(**result)
    except Exception as e:
        logger.error(f"Failed to list datasets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to list datasets",
        )


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str) -> DatasetResponse:
    """Get dataset by ID."""
    try:
        dataset = await dataset_service.get_dataset(dataset_id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found",
            )
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get dataset",
        )


@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
async def get_dataset_preview(
    dataset_id: str,
    num_rows: int = Query(5, ge=1, le=100),
) -> DatasetPreview:
    """Get preview of dataset."""
    try:
        preview = await dataset_service.get_dataset_preview(
            dataset_id=dataset_id,
            num_rows=num_rows,
        )
        if not preview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot preview dataset {dataset_id}",
            )
        return DatasetPreview(**preview)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to preview dataset",
        )


@router.patch("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    dataset_update: DatasetUpdate,
) -> DatasetResponse:
    """Update dataset metadata."""
    try:
        if dataset_update.metadata:
            result = await dataset_service.update_dataset_metadata(
                dataset_id=dataset_id,
                metadata=dataset_update.metadata,
            )
            return result
        else:
            dataset = await dataset_service.get_dataset(dataset_id)
            if not dataset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dataset {dataset_id} not found",
                )
            return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update dataset",
        )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(dataset_id: str):
    """Delete a dataset."""
    try:
        success = await dataset_service.delete_dataset(dataset_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dataset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete dataset",
        )
