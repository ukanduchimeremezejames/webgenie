"""
Inference service for running GRN algorithms.
"""

import os
import json
import subprocess
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class InferenceService:
    """Service for running GRN inference algorithms."""

    def __init__(self):
        """Initialize inference service."""
        self.results_dir = settings.RESULTS_DIR
        self.temp_dir = settings.TEMP_DIR
        self.docker_registry = settings.DOCKER_REGISTRY
        self.use_docker = settings.USE_DOCKER

    def _get_docker_image(self, algorithm: str) -> str:
        """Get Docker image name for algorithm."""
        algorithm_lower = algorithm.lower()
        return f"{self.docker_registry}/{algorithm_lower}"

    def _create_job_directory(self, job_id: str) -> Path:
        """Create job-specific directory."""
        job_dir = self.results_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    async def run_algorithm(
        self,
        job_id: str,
        dataset_id: str,
        algorithm: str,
        dataset_path: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run a GRN inference algorithm."""
        try:
            job_dir = self._create_job_directory(job_id)
            log_file = job_dir / "execution.log"
            output_file = job_dir / f"{algorithm.lower()}_network.tsv"

            logger.info(
                f"Starting inference with {algorithm}",
                extra={"job_id": job_id, "algorithm": algorithm, "dataset_id": dataset_id},
            )

            # Prepare command based on algorithm
            cmd = self._prepare_algorithm_command(
                algorithm=algorithm,
                dataset_path=dataset_path,
                output_path=str(output_file),
                parameters=parameters,
                job_dir=str(job_dir),
            )

            # Run algorithm
            with open(log_file, "w") as lf:
                process = await self._execute_command(cmd, lf)

            if process.returncode != 0:
                error_msg = f"Algorithm execution failed with code {process.returncode}"
                logger.error(
                    error_msg,
                    extra={"job_id": job_id, "algorithm": algorithm},
                )
                raise RuntimeError(error_msg)

            # Validate output
            if not output_file.exists():
                raise RuntimeError(f"Output file not created: {output_file}")

            # Generate result summary
            result = {
                "job_id": job_id,
                "dataset_id": dataset_id,
                "algorithm": algorithm,
                "status": "completed",
                "output_file": str(output_file),
                "log_file": str(log_file),
                "completed_at": datetime.utcnow().isoformat(),
                "metrics": await self._compute_metrics(output_file, dataset_path),
            }

            logger.info(
                f"Algorithm execution completed",
                extra={"job_id": job_id, "algorithm": algorithm},
            )

            return result

        except Exception as e:
            logger.error(
                f"Algorithm execution failed: {str(e)}",
                extra={"job_id": job_id, "algorithm": algorithm},
            )
            raise

    def _prepare_algorithm_command(
        self,
        algorithm: str,
        dataset_path: str,
        output_path: str,
        parameters: Dict[str, Any],
        job_dir: str,
    ) -> list:
        """Prepare command for algorithm execution."""
        if self.use_docker:
            return self._prepare_docker_command(
                algorithm, dataset_path, output_path, parameters, job_dir
            )
        else:
            return self._prepare_python_command(
                algorithm, dataset_path, output_path, parameters, job_dir
            )

    def _prepare_docker_command(
        self,
        algorithm: str,
        dataset_path: str,
        output_path: str,
        parameters: Dict[str, Any],
        job_dir: str,
    ) -> list:
        """Prepare Docker command for algorithm."""
        docker_image = self._get_docker_image(algorithm)
        
        # Volume mappings
        volumes = [
            f"{dataset_path}:/data/input:ro",
            f"{output_path}:/data/output/network.tsv",
            f"{job_dir}:/data/logs",
        ]

        # Base docker command
        cmd = ["docker", "run", "--rm"]

        # Add volume mounts
        for volume in volumes:
            cmd.extend(["-v", volume])

        # Add memory limit
        cmd.extend(["-m", settings.ALGORITHM_MEMORY_LIMIT])

        # Add image and default script
        cmd.append(docker_image)

        # Algorithm-specific parameters would be added here
        # This is a generic template
        cmd.extend([
            "bash", "-c",
            f"cd /data && python run{algorithm}.py --input /data/input --output /data/output"
        ])

        return cmd

    def _prepare_python_command(
        self,
        algorithm: str,
        dataset_path: str,
        output_path: str,
        parameters: Dict[str, Any],
        job_dir: str,
    ) -> list:
        """Prepare Python command for algorithm."""
        # This would use the refactored Python runners from BLRun
        runner_module = self._get_python_runner(algorithm)
        
        cmd = [
            "python",
            "-m",
            runner_module,
            "--input",
            dataset_path,
            "--output",
            output_path,
            "--log",
            str(Path(job_dir) / "execution.log"),
        ]

        # Add parameters
        for key, value in parameters.items():
            cmd.extend([f"--{key}", str(value)])

        return cmd

    def _get_python_runner(self, algorithm: str) -> str:
        """Get Python runner module for algorithm."""
        runner_map = {
            "SCODE": "app.services.runners.scode_runner",
            "SCNS": "app.services.runners.scns_runner",
            "SINCERITIES": "app.services.runners.sincerities_runner",
            "PIDC": "app.services.runners.pidc_runner",
            "GRNVBEM": "app.services.runners.grnvbem_runner",
            "GENIE3": "app.services.runners.genie3_runner",
            "GRNBOOST2": "app.services.runners.grnboost2_runner",
            "LEAP": "app.services.runners.leap_runner",
            "JUMP3": "app.services.runners.jump3_runner",
            "PPCOR": "app.services.runners.ppcor_runner",
            "GRISLI": "app.services.runners.grisli_runner",
            "SINGE": "app.services.runners.singe_runner",
            "SCRIBE": "app.services.runners.scribe_runner",
            "SCSGL": "app.services.runners.scsgl_runner",
        }
        
        return runner_map.get(algorithm.upper(), "app.services.runners.generic_runner")

    async def _execute_command(self, cmd: list, log_file) -> subprocess.CompletedProcess:
        """Execute command and capture output."""
        try:
            process = subprocess.run(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                timeout=settings.ALGORITHM_TIMEOUT,
            )
            return process
        except subprocess.TimeoutExpired:
            logger.error("Algorithm execution timeout")
            raise RuntimeError("Algorithm execution timed out")

    async def _compute_metrics(
        self,
        output_file: Path,
        dataset_path: str,
    ) -> Dict[str, Any]:
        """Compute metrics for result."""
        try:
            # Parse network file
            import pandas as pd
            
            network_df = pd.read_csv(output_file, sep="\t", header=None)
            
            metrics = {
                "total_edges": len(network_df),
                "num_unique_genes": len(set(network_df[0]) | set(network_df[1])),
            }
            
            return metrics
        except Exception as e:
            logger.warning(f"Failed to compute metrics: {str(e)}")
            return {}


# Global service instance
inference_service = InferenceService()
