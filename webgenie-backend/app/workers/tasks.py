"""
Celery task definitions for asynchronous job execution.
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from app.core.tasks import celery_app
from app.services.inference_service import inference_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.workers.tasks.run_inference_job")
def run_inference_job(
    self,
    job_id: str,
    dataset_id: str,
    algorithm: str,
    dataset_path: str,
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    """Run GRN inference job asynchronously."""
    try:
        logger.info(
            f"Starting inference task",
            extra={"job_id": job_id, "algorithm": algorithm},
        )

        # Update task state to running
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Initializing algorithm"},
        )

        # Run algorithm
        result = inference_service.run_algorithm(
            job_id=job_id,
            dataset_id=dataset_id,
            algorithm=algorithm,
            dataset_path=dataset_path,
            parameters=parameters,
        )

        logger.info(
            f"Inference task completed",
            extra={"job_id": job_id, "algorithm": algorithm},
        )

        return result

    except Exception as e:
        logger.error(
            f"Inference task failed: {str(e)}",
            extra={"job_id": job_id, "algorithm": algorithm},
        )
        self.update_state(
            state="FAILURE",
            meta={
                "exc_type": type(e).__name__,
                "exc_message": str(e),
            },
        )
        raise


@celery_app.task(bind=True, name="app.workers.tasks.compare_networks")
def compare_networks(
    self,
    network_file_1: str,
    network_file_2: str,
) -> Dict[str, Any]:
    """Compare two GRN networks."""
    try:
        import pandas as pd

        logger.info("Starting network comparison")

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

        result = {
            "jaccard_index": float(jaccard_index),
            "overlap_edges": len(intersection),
            "edges_only_in_1": len(edges1 - edges2),
            "edges_only_in_2": len(edges2 - edges1),
            "total_edges_1": len(edges1),
            "total_edges_2": len(edges2),
        }

        logger.info(f"Network comparison completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Network comparison failed: {str(e)}")
        raise


@celery_app.task(
    name="app.workers.tasks.cleanup_old_results",
    expires=3600,
)
def cleanup_old_results(days: int = 7) -> Dict[str, Any]:
    """Clean up old result files."""
    try:
        from app.core.config import settings
        import shutil

        logger.info(f"Starting cleanup of results older than {days} days")

        results_dir = settings.RESULTS_DIR
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0
        deleted_size = 0

        for job_dir in results_dir.iterdir():
            if not job_dir.is_dir():
                continue

            # Check if directory is older than cutoff
            mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
            if mtime < cutoff_time:
                try:
                    size = sum(
                        f.stat().st_size
                        for f in job_dir.rglob("*")
                        if f.is_file()
                    )
                    shutil.rmtree(job_dir)
                    deleted_count += 1
                    deleted_size += size
                    logger.info(f"Deleted old results: {job_dir.name}")
                except Exception as e:
                    logger.error(f"Failed to delete {job_dir}: {str(e)}")

        logger.info(
            f"Cleanup completed: {deleted_count} directories, "
            f"{deleted_size / (1024 * 1024):.2f} MB freed"
        )

        return {
            "deleted_count": deleted_count,
            "freed_mb": deleted_size / (1024 * 1024),
        }

    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        raise


@celery_app.task(name="app.workers.tasks.compute_metrics")
def compute_metrics(result_file: str) -> Dict[str, Any]:
    """Compute metrics for a result network."""
    try:
        import pandas as pd

        logger.info(f"Computing metrics for {result_file}")

        network = pd.read_csv(result_file, sep="\t", header=None)

        # Compute basic network metrics
        num_edges = len(network)
        nodes = set(network[0]) | set(network[1])
        num_nodes = len(nodes)
        density = (2 * num_edges) / (num_nodes * (num_nodes - 1))

        # Degree statistics
        degree_dict = {}
        for _, row in network.iterrows():
            degree_dict[row[0]] = degree_dict.get(row[0], 0) + 1
            degree_dict[row[1]] = degree_dict.get(row[1], 0) + 1

        degrees = list(degree_dict.values())
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0

        metrics = {
            "total_edges": int(num_edges),
            "num_nodes": int(num_nodes),
            "density": float(density),
            "avg_degree": float(avg_degree),
            "max_degree": int(max_degree),
        }

        logger.info(f"Metrics computed: {metrics}")
        return metrics

    except Exception as e:
        logger.error(f"Metrics computation failed: {str(e)}")
        raise


@celery_app.task(name="app.workers.tasks.export_results")
def export_results(job_id: str, export_format: str = "json") -> Dict[str, Any]:
    """Export job results in specified format."""
    try:
        from app.core.config import settings

        logger.info(f"Exporting results for job {job_id} in {export_format} format")

        job_dir = settings.RESULTS_DIR / job_id
        if not job_dir.exists():
            raise FileNotFoundError(f"Job directory not found: {job_dir}")

        export_dir = job_dir / f"export_{export_format}"
        export_dir.mkdir(parents=True, exist_ok=True)

        # Copy and convert files based on format
        network_file = None
        for f in job_dir.glob("*_network.*"):
            if f.is_file():
                network_file = f
                break

        if network_file is None:
            raise FileNotFoundError("No network file found in job directory")

        if export_format == "json":
            import pandas as pd
            import json

            network = pd.read_csv(network_file, sep="\t", header=None)
            export_file = export_dir / "network.json"

            data = {
                "edges": [
                    {"source": row[0], "target": row[1], "weight": row[2] if len(row) > 2 else 1.0}
                    for _, row in network.iterrows()
                ]
            }

            with open(export_file, "w") as f:
                json.dump(data, f, indent=2)

        elif export_format == "graphml":
            import pandas as pd
            import networkx as nx

            network = pd.read_csv(network_file, sep="\t", header=None)
            G = nx.DiGraph()

            for _, row in network.iterrows():
                weight = row[2] if len(row) > 2 else 1.0
                G.add_edge(row[0], row[1], weight=weight)

            export_file = export_dir / "network.graphml"
            nx.write_graphml(G, str(export_file))

        logger.info(f"Results exported to {export_file}")

        return {
            "export_format": export_format,
            "export_file": str(export_file),
        }

    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise
