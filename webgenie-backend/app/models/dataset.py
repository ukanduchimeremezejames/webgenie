"""
Pydantic models for Dataset management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DatasetSource(BaseModel):
    """Dataset source information."""

    source_type: str = Field(..., description="Source type (huggingface, local, etc.)")
    url: str = Field(..., description="Dataset URL or path")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source metadata")


class DatasetSchema(BaseModel):
    """Dataset schema information."""

    gene_column: str = Field(..., description="Column name for genes")
    cell_column: str = Field(..., description="Column name for cells")
    expression_column: str = Field(..., description="Column name for expression values")
    metadata_columns: List[str] = Field(default_factory=list, description="Metadata columns")


class DatasetBase(BaseModel):
    """Base dataset model."""

    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(default=None, description="Dataset description")
    species: Optional[str] = Field(default=None, description="Species name")
    tissue: Optional[str] = Field(default=None, description="Tissue type")
    num_genes: Optional[int] = Field(default=None, description="Number of genes")
    num_cells: Optional[int] = Field(default=None, description="Number of cells")


class DatasetCreate(DatasetBase):
    """Model for creating a dataset."""

    source: DatasetSource = Field(..., description="Dataset source")
    schema: DatasetSchema = Field(..., description="Dataset schema")


class DatasetUpdate(BaseModel):
    """Model for updating a dataset."""

    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DatasetResponse(DatasetBase):
    """Model for dataset response."""

    id: str = Field(..., description="Dataset unique identifier")
    source: DatasetSource = Field(..., description="Dataset source")
    schema: DatasetSchema = Field(..., description="Dataset schema")
    file_path: Optional[str] = Field(default=None, description="Path to dataset file")
    file_size: Optional[int] = Field(default=None, description="Dataset file size in bytes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Model config."""

        from_attributes = True


class DatasetListResponse(BaseModel):
    """Model for dataset list response."""

    total: int = Field(..., description="Total number of datasets")
    items: List[DatasetResponse] = Field(..., description="Dataset list")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")


class DatasetPreview(BaseModel):
    """Model for dataset preview."""

    id: str = Field(..., description="Dataset ID")
    name: str = Field(..., description="Dataset name")
    num_rows: int = Field(..., description="Number of rows")
    num_columns: int = Field(..., description="Number of columns")
    columns: List[str] = Field(..., description="Column names")
    sample_data: List[Dict[str, Any]] = Field(..., description="Sample data rows")
