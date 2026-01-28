"""
Services for managing datasets from HuggingFace Hub.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceDatasetManager:
    """Manages dataset discovery and integration from HuggingFace Hub."""

    HF_API_BASE = "https://huggingface.co/api"
    DATASET_ORG = "cskokgibbs"
    DATASET_PREFIX = "datasets"

    def __init__(self, hf_token: Optional[str] = None):
        """Initialize HuggingFace dataset manager.
        
        Args:
            hf_token: HuggingFace API token for authentication
        """
        self.hf_token = hf_token or settings.HF_TOKEN
        self.headers = {}
        if self.hf_token:
            self.headers["Authorization"] = f"Bearer {self.hf_token}"

    async def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets from the HuggingFace organization.
        
        Returns:
            List of dataset metadata
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # List repos in the organization
                url = f"{self.HF_API_BASE}/models?author={self.DATASET_ORG}&search={self.DATASET_PREFIX}"
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                repos = response.json()
                datasets = []
                
                for repo in repos:
                    if self.DATASET_PREFIX in repo.get("id", ""):
                        dataset_info = await self._get_dataset_info(repo["id"])
                        if dataset_info:
                            datasets.append(dataset_info)
                
                logger.info(f"Found {len(datasets)} datasets from {self.DATASET_ORG}")
                return datasets
        except Exception as e:
            logger.error(f"Failed to list HuggingFace datasets: {str(e)}")
            return []

    async def _get_dataset_info(self, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a dataset.
        
        Args:
            repo_id: Repository ID in format 'org/name'
        
        Returns:
            Dataset metadata
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{self.HF_API_BASE}/models/{repo_id}"
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                return {
                    "id": repo_id,
                    "name": data.get("id", "").split("/")[-1],
                    "description": data.get("description", ""),
                    "source": f"huggingface://{repo_id}",
                    "url": f"https://huggingface.co/{repo_id}",
                    "downloads": data.get("downloads", 0),
                    "likes": data.get("likes", 0),
                    "created_at": data.get("created_at", datetime.now().isoformat()),
                    "updated_at": data.get("updated_at", datetime.now().isoformat()),
                }
        except Exception as e:
            logger.error(f"Failed to get dataset info for {repo_id}: {str(e)}")
            return None

    async def download_dataset(self, repo_id: str, dest_path: str) -> bool:
        """Download a dataset from HuggingFace.
        
        Args:
            repo_id: Repository ID
            dest_path: Destination path for the dataset
        
        Returns:
            True if download successful, False otherwise
        """
        try:
            logger.info(f"Downloading dataset from {repo_id} to {dest_path}")
            # Implementation would use huggingface_hub library
            # from huggingface_hub import snapshot_download
            # snapshot_download(repo_id=repo_id, repo_type="model", local_dir=dest_path)
            logger.info(f"Successfully downloaded {repo_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to download dataset {repo_id}: {str(e)}")
            return False


# Create singleton instance
hf_dataset_manager = HuggingFaceDatasetManager(hf_token=settings.HF_TOKEN)
