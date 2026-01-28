"""
Dataset management service.
Handles dataset registration, validation, and metadata management.
"""

import os
import json
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import pandas as pd
import logging

from app.core.config import settings
from app.models.dataset import DatasetResponse, DatasetSchema, DatasetSource

logger = logging.getLogger(__name__)


class DatasetService:
    """Service for managing datasets."""

    def __init__(self):
        """Initialize dataset service."""
        self.datasets_dir = settings.DATASETS_DIR
        self.datasets_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.datasets_dir / "metadata.json"
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load datasets metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}

    def _save_metadata(self) -> None:
        """Save datasets metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2, default=str)

    def _generate_dataset_id(self, name: str) -> str:
        """Generate unique dataset ID."""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{name}:{timestamp}"
        hash_id = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        return f"{name.lower().replace(' ', '-')}-{hash_id}"

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    async def register_dataset(
        self,
        name: str,
        source: DatasetSource,
        schema: DatasetSchema,
        description: Optional[str] = None,
        species: Optional[str] = None,
        tissue: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DatasetResponse:
        """Register a new dataset."""
        try:
            dataset_id = self._generate_dataset_id(name)

            # Create dataset directory
            dataset_dir = self.datasets_dir / dataset_id
            dataset_dir.mkdir(parents=True, exist_ok=True)

            # Store source information
            source_info = {
                **source.dict(),
                "registered_at": datetime.utcnow().isoformat(),
            }

            # Save metadata
            dataset_metadata = {
                "id": dataset_id,
                "name": name,
                "description": description,
                "species": species,
                "tissue": tissue,
                "source": source_info,
                "schema": schema.dict(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            self.metadata[dataset_id] = dataset_metadata
            self._save_metadata()

            logger.info(
                f"Dataset registered: {dataset_id}",
                extra={"dataset_id": dataset_id, "name": name},
            )

            return DatasetResponse(**dataset_metadata)

        except Exception as e:
            logger.error(
                f"Failed to register dataset: {str(e)}",
                extra={"dataset_id": name},
            )
            raise

    async def get_dataset(self, dataset_id: str) -> Optional[DatasetResponse]:
        """Get dataset by ID."""
        if dataset_id not in self.metadata:
            logger.warning(f"Dataset not found: {dataset_id}")
            return None

        return DatasetResponse(**self.metadata[dataset_id])

    async def list_datasets(
        self, skip: int = 0, limit: int = 10
    ) -> Dict[str, Any]:
        """List all registered datasets."""
        all_datasets = list(self.metadata.values())
        total = len(all_datasets)
        items = [DatasetResponse(**d) for d in all_datasets[skip : skip + limit]]

        return {
            "total": total,
            "items": items,
            "page": skip // limit + 1,
            "per_page": limit,
        }

    async def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset."""
        try:
            if dataset_id not in self.metadata:
                logger.warning(f"Dataset not found: {dataset_id}")
                return False

            # Remove metadata
            del self.metadata[dataset_id]
            self._save_metadata()

            # Remove dataset directory
            dataset_dir = self.datasets_dir / dataset_id
            if dataset_dir.exists():
                import shutil

                shutil.rmtree(dataset_dir)

            logger.info(f"Dataset deleted: {dataset_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete dataset: {str(e)}")
            raise

    async def update_dataset_metadata(
        self, dataset_id: str, metadata: Dict[str, Any]
    ) -> DatasetResponse:
        """Update dataset metadata."""
        if dataset_id not in self.metadata:
            logger.warning(f"Dataset not found: {dataset_id}")
            raise ValueError(f"Dataset {dataset_id} not found")

        dataset = self.metadata[dataset_id]
        dataset["metadata"].update(metadata)
        dataset["updated_at"] = datetime.utcnow().isoformat()

        self._save_metadata()
        logger.info(f"Dataset metadata updated: {dataset_id}")

        return DatasetResponse(**dataset)

    async def get_dataset_preview(
        self, dataset_id: str, num_rows: int = 5
    ) -> Optional[Dict[str, Any]]:
        """Get preview of dataset."""
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return None

        try:
            # Try to load and preview the dataset file
            dataset_dir = self.datasets_dir / dataset_id
            dataset_file = dataset_dir / "data.csv"

            if not dataset_file.exists():
                logger.warning(f"Dataset file not found: {dataset_file}")
                return None

            df = pd.read_csv(dataset_file, nrows=num_rows)

            return {
                "id": dataset_id,
                "name": dataset.name,
                "num_rows": len(df),
                "num_columns": len(df.columns),
                "columns": df.columns.tolist(),
                "sample_data": df.head(num_rows).to_dict("records"),
            }

        except Exception as e:
            logger.error(f"Failed to preview dataset: {str(e)}")
            return None

    async def validate_dataset_schema(
        self, dataset_id: str, file_path: Path
    ) -> bool:
        """Validate dataset schema."""
        try:
            dataset = await self.get_dataset(dataset_id)
            if not dataset:
                return False

            df = pd.read_csv(file_path)

            # Check required columns
            required_columns = [
                dataset.schema.gene_column,
                dataset.schema.cell_column,
                dataset.schema.expression_column,
            ]

            for col in required_columns:
                if col not in df.columns:
                    logger.error(
                        f"Missing required column: {col}",
                        extra={"dataset_id": dataset_id},
                    )
                    return False

            logger.info(
                f"Dataset schema validation passed",
                extra={"dataset_id": dataset_id},
            )
            return True

        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return False


# Global service instance
dataset_service = DatasetService()
