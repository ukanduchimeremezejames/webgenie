"""
Pydantic models for Result management.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ResultMetrics(BaseModel):
    """Result metrics."""

    auc_roc: Optional[float] = Field(default=None, description="AUC-ROC score")
    auc_pr: Optional[float] = Field(default=None, description="AUC-PR score")
    mcc: Optional[float] = Field(default=None, description="Matthew's correlation coefficient")
    precision: Optional[float] = Field(default=None, description="Precision")
    recall: Optional[float] = Field(default=None, description="Recall")
    f1_score: Optional[float] = Field(default=None, description="F1 score")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")


class ResultBase(BaseModel):
    """Base result model."""

    job_id: str = Field(..., description="Associated job ID")
    dataset_id: str = Field(..., description="Associated dataset ID")
    algorithm: str = Field(..., description="Algorithm name")


class ResultCreate(ResultBase):
    """Model for creating a result."""

    network_file: str = Field(..., description="Path to network file")
    summary: Optional[Dict[str, Any]] = Field(default=None, description="Result summary")
    metrics: Optional[ResultMetrics] = Field(default=None, description="Computed metrics")


class ResultResponse(ResultBase):
    """Model for result response."""

    id: str = Field(..., description="Result unique identifier")
    network_file: str = Field(..., description="Path to network file")
    summary: Optional[Dict[str, Any]] = Field(default=None, description="Result summary")
    metrics: Optional[ResultMetrics] = Field(default=None, description="Computed metrics")
    created_at: datetime = Field(..., description="Creation timestamp")
    file_size: Optional[int] = Field(default=None, description="Network file size in bytes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        """Model config."""

        from_attributes = True


class ResultListResponse(BaseModel):
    """Model for result list response."""

    total: int = Field(..., description="Total number of results")
    items: List[ResultResponse] = Field(..., description="Result list")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")


class NetworkComparison(BaseModel):
    """Network comparison result."""

    network1_id: str = Field(..., description="First network result ID")
    network2_id: str = Field(..., description="Second network result ID")
    jaccard_index: float = Field(..., description="Jaccard similarity index")
    overlap_edges: int = Field(..., description="Number of overlapping edges")
    edges_only_in_1: int = Field(..., description="Edges only in first network")
    edges_only_in_2: int = Field(..., description="Edges only in second network")


class ResultSummary(BaseModel):
    """Summary of result statistics."""

    total_edges: int = Field(..., description="Total number of edges")
    num_nodes: int = Field(..., description="Number of nodes")
    density: float = Field(..., description="Network density")
    avg_degree: float = Field(..., description="Average degree")
    max_degree: int = Field(..., description="Maximum degree")
