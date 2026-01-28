"""
API endpoints for result management.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status, FileResponse
from fastapi.responses import StreamingResponse
import logging
from pathlib import Path

from app.models.result import (
    ResultResponse,
    ResultListResponse,
    NetworkComparison,
    ResultSummary,
)
from app.workers.tasks import compute_metrics, compare_networks, export_results

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/results", tags=["results"])


@router.get("/job/{job_id}", response_model=ResultResponse)
async def get_job_result(job_id: str) -> ResultResponse:
    """Get result for a job."""
    try:
        from app.core.config import settings

        job_dir = settings.RESULTS_DIR / job_id
        if not job_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Result for job {job_id} not found",
            )

        # Find network file
        network_file = None
        for f in job_dir.glob("*_network.*"):
            if f.is_file():
                network_file = f
                break

        if not network_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Network file not found",
            )

        result_data = {
            "id": job_id,
            "job_id": job_id,
            "dataset_id": "unknown",
            "algorithm": "unknown",
            "network_file": str(network_file),
            "created_at": datetime.utcnow(),
        }

        return ResultResponse(**result_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get result",
        )


@router.get("/job/{job_id}/summary", response_model=ResultSummary)
async def get_result_summary(job_id: str) -> ResultSummary:
    """Get result summary."""
    try:
        from app.core.config import settings
        import pandas as pd

        job_dir = settings.RESULTS_DIR / job_id

        # Find network file
        network_file = None
        for f in job_dir.glob("*_network.*"):
            if f.is_file():
                network_file = f
                break

        if not network_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Network file not found",
            )

        # Compute metrics
        network = pd.read_csv(network_file, sep="\t", header=None)
        num_edges = len(network)
        nodes = set(network[0]) | set(network[1])
        num_nodes = len(nodes)

        # Compute density
        density = (2 * num_edges) / (num_nodes * (num_nodes - 1)) if num_nodes > 1 else 0

        # Compute degree statistics
        degree_dict = {}
        for _, row in network.iterrows():
            degree_dict[row[0]] = degree_dict.get(row[0], 0) + 1
            degree_dict[row[1]] = degree_dict.get(row[1], 0) + 1

        degrees = list(degree_dict.values())
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0

        summary = ResultSummary(
            total_edges=num_edges,
            num_nodes=num_nodes,
            density=float(density),
            avg_degree=float(avg_degree),
            max_degree=int(max_degree),
        )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compute summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to compute summary",
        )


@router.post("/compare", response_model=NetworkComparison)
async def compare_result_networks(
    job_id_1: str,
    job_id_2: str,
) -> NetworkComparison:
    """Compare two result networks."""
    try:
        from app.core.config import settings
        import pandas as pd

        # Find network files
        def get_network_file(job_id: str) -> Path:
            job_dir = settings.RESULTS_DIR / job_id
            for f in job_dir.glob("*_network.*"):
                if f.is_file():
                    return f
            raise FileNotFoundError(f"Network file for job {job_id}")

        network_file_1 = get_network_file(job_id_1)
        network_file_2 = get_network_file(job_id_2)

        # Load networks
        net1 = pd.read_csv(network_file_1, sep="\t", header=None)
        net2 = pd.read_csv(network_file_2, sep="\t", header=None)

        # Convert to edge sets
        edges1 = set(zip(net1[0], net1[1]))
        edges2 = set(zip(net2[0], net2[1]))

        # Compute metrics
        intersection = edges1 & edges2
        union = edges1 | edges2
        jaccard_index = len(intersection) / len(union) if len(union) > 0 else 0

        comparison = NetworkComparison(
            network1_id=job_id_1,
            network2_id=job_id_2,
            jaccard_index=float(jaccard_index),
            overlap_edges=len(intersection),
            edges_only_in_1=len(edges1 - edges2),
            edges_only_in_2=len(edges2 - edges1),
        )

        return comparison

    except Exception as e:
        logger.error(f"Failed to compare networks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to compare networks",
        )


@router.get("/job/{job_id}/network/download")
async def download_network(job_id: str, format: str = "tsv"):
    """Download network file."""
    try:
        from app.core.config import settings

        job_dir = settings.RESULTS_DIR / job_id

        # Find network file
        network_file = None
        for f in job_dir.glob("*_network.*"):
            if f.is_file():
                network_file = f
                break

        if not network_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Network file not found",
            )

        if format.lower() == "json":
            import pandas as pd
            import json

            network = pd.read_csv(network_file, sep="\t", header=None)
            data = {
                "edges": [
                    {
                        "source": row[0],
                        "target": row[1],
                        "weight": float(row[2]) if len(row) > 2 else 1.0,
                    }
                    for _, row in network.iterrows()
                ]
            }

            from io import BytesIO

            output = BytesIO()
            output.write(json.dumps(data).encode())
            output.seek(0)

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=network.json"
                },
            )
        else:
            return FileResponse(
                network_file,
                media_type="text/tab-separated-values",
                filename=f"network.tsv",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download network: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to download network",
        )


@router.post("/job/{job_id}/export")
async def export_job_results(
    job_id: str,
    export_format: str = Query("json", regex="^(json|graphml|csv)$"),
):
    """Export job results in specified format."""
    try:
        task = export_results.delay(job_id=job_id, export_format=export_format)

        return {
            "task_id": task.id,
            "job_id": job_id,
            "export_format": export_format,
            "status": "processing",
        }

    except Exception as e:
        logger.error(f"Failed to export results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to export results",
        )


from datetime import datetime
