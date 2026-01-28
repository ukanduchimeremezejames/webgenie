"""
Services for managing algorithms from Docker Hub and running them in containers.
"""

import logging
import json
from typing import Optional, List, Dict, Any
import httpx
import docker
from docker.types import Mount
from app.core.config import settings

logger = logging.getLogger(__name__)


class DockerHubAlgorithmManager:
    """Manages algorithm discovery and execution from Docker Hub."""

    DOCKER_HUB_API = "https://hub.docker.com/v2"
    REGISTRY = "grnbeeline"

    # Known GRN algorithms available on Docker Hub
    ALGORITHMS = {
        "scode": {
            "description": "SCODE - Single-Cell Optimal Experimental Design",
            "docker_image": "grnbeeline/scode:latest",
            "parameters": {
                "num_runs": {"type": "integer", "default": 10, "description": "Number of runs"},
                "seed": {"type": "integer", "default": 42, "description": "Random seed"},
            },
        },
        "scns": {
            "description": "SCNS - Single-Cell Network Synthesis",
            "docker_image": "grnbeeline/scns:latest",
            "parameters": {
                "alpha": {"type": "number", "default": 0.1, "description": "Regularization parameter"},
            },
        },
        "sincerities": {
            "description": "SINCERITIES - Single-Cell Network Inference",
            "docker_image": "grnbeeline/sincerities:latest",
            "parameters": {
                "delta_t": {"type": "number", "default": 1.0, "description": "Time step"},
            },
        },
        "pidc": {
            "description": "PIDC - Partial Information Decomposition and Context",
            "docker_image": "grnbeeline/pidc:latest",
            "parameters": {},
        },
        "grnvbem": {
            "description": "GRNVBEM - Gene Regulatory Network Variational Bayes EM",
            "docker_image": "grnbeeline/grnvbem:latest",
            "parameters": {
                "max_iter": {"type": "integer", "default": 100, "description": "Maximum iterations"},
            },
        },
        "genie3": {
            "description": "GENIE3 - GRN Inference using Ensemble Regression Trees",
            "docker_image": "grnbeeline/genie3:latest",
            "parameters": {
                "n_trees": {"type": "integer", "default": 1000, "description": "Number of trees"},
            },
        },
        "grnboost2": {
            "description": "GRNBOOST2 - GRN Inference using Gradient Boosting",
            "docker_image": "grnbeeline/grnboost2:latest",
            "parameters": {
                "n_jobs": {"type": "integer", "default": -1, "description": "Number of parallel jobs"},
            },
        },
        "leap": {
            "description": "LEAP - Linear Equation Assumption Propagation",
            "docker_image": "grnbeeline/leap:latest",
            "parameters": {
                "lambda": {"type": "number", "default": 0.01, "description": "Regularization parameter"},
            },
        },
        "jump3": {
            "description": "JUMP3 - Jump3 GRN inference",
            "docker_image": "grnbeeline/jump3:latest",
            "parameters": {},
        },
        "ppcor": {
            "description": "PPCOR - Partial Pearson Correlation",
            "docker_image": "grnbeeline/ppcor:latest",
            "parameters": {
                "method": {"type": "string", "default": "pearson", "description": "Correlation method"},
            },
        },
        "grisli": {
            "description": "GRISLI - GRN using Sparse Linear Model",
            "docker_image": "grnbeeline/grisli:latest",
            "parameters": {
                "alpha": {"type": "number", "default": 1.0, "description": "Elastic net alpha"},
            },
        },
        "singe": {
            "description": "SINGE - Sparse Inverse covariance estimation for Network Generation",
            "docker_image": "grnbeeline/singe:latest",
            "parameters": {},
        },
    }

    def __init__(self):
        """Initialize Docker Hub algorithm manager."""
        try:
            self.docker_client = docker.from_env()
            logger.info("Connected to Docker daemon")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {str(e)}")
            self.docker_client = None

    async def list_algorithms(self) -> List[Dict[str, Any]]:
        """List all available algorithms.
        
        Returns:
            List of algorithm metadata
        """
        algorithms = []
        for name, info in self.ALGORITHMS.items():
            algorithms.append({
                "name": name,
                "description": info.get("description", ""),
                "docker_image": info.get("docker_image", ""),
                "parameters": info.get("parameters", {}),
                "registry": self.REGISTRY,
            })
        
        logger.info(f"Available {len(algorithms)} algorithms")
        return algorithms

    async def get_algorithm(self, algorithm_name: str) -> Optional[Dict[str, Any]]:
        """Get algorithm details.
        
        Args:
            algorithm_name: Name of the algorithm
        
        Returns:
            Algorithm metadata
        """
        algo_info = self.ALGORITHMS.get(algorithm_name.lower())
        if not algo_info:
            logger.warning(f"Algorithm {algorithm_name} not found")
            return None
        
        return {
            "name": algorithm_name.lower(),
            "description": algo_info.get("description", ""),
            "docker_image": algo_info.get("docker_image", ""),
            "parameters": algo_info.get("parameters", {}),
            "registry": self.REGISTRY,
        }

    def run_algorithm(
        self,
        algorithm_name: str,
        input_file: str,
        output_dir: str,
        parameters: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """Run an algorithm in a Docker container.
        
        Args:
            algorithm_name: Name of the algorithm
            input_file: Path to input dataset file
            output_dir: Directory for output results
            parameters: Algorithm parameters
            timeout: Execution timeout in seconds
        
        Returns:
            True if execution successful, False otherwise
        """
        if not self.docker_client:
            logger.error("Docker client not available")
            return False

        algo_info = self.ALGORITHMS.get(algorithm_name.lower())
        if not algo_info:
            logger.error(f"Algorithm {algorithm_name} not found")
            return False

        docker_image = algo_info["docker_image"]
        timeout = timeout or settings.ALGORITHM_TIMEOUT

        try:
            logger.info(f"Running {algorithm_name} with image {docker_image}")

            # Pull the image if not available locally
            try:
                self.docker_client.images.pull(docker_image)
                logger.info(f"Pulled image {docker_image}")
            except Exception as e:
                logger.warning(f"Failed to pull image: {str(e)}")

            # Prepare command
            cmd = [
                "python",
                "-m",
                algorithm_name.lower(),
                f"--input={input_file}",
                f"--output={output_dir}",
            ]

            # Add parameters to command
            if parameters:
                for key, value in parameters.items():
                    cmd.append(f"--{key}={value}")

            # Run container
            container = self.docker_client.containers.run(
                docker_image,
                command=cmd,
                volumes=[
                    Mount(source=input_file, target="/data/input.csv", type="bind", read_only=True),
                    Mount(source=output_dir, target="/data/output", type="bind"),
                ],
                mem_limit=settings.ALGORITHM_MEMORY_LIMIT,
                timeout=timeout,
                remove=True,
                detach=False,
            )

            logger.info(f"Successfully executed {algorithm_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to run algorithm {algorithm_name}: {str(e)}")
            return False

    async def check_image_available(self, algorithm_name: str) -> bool:
        """Check if algorithm Docker image is available.
        
        Args:
            algorithm_name: Name of the algorithm
        
        Returns:
            True if image available, False otherwise
        """
        if not self.docker_client:
            return False

        algo_info = self.ALGORITHMS.get(algorithm_name.lower())
        if not algo_info:
            return False

        docker_image = algo_info["docker_image"]

        try:
            self.docker_client.images.get(docker_image)
            return True
        except Exception:
            return False


# Create singleton instance
algorithm_manager = DockerHubAlgorithmManager()
