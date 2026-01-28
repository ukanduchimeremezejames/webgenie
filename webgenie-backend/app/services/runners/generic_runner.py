"""
Generic algorithm runner that can be extended for specific algorithms.
"""

from typing import Dict, Any, Optional
import pandas as pd
import logging

from app.services.runners.utils import BaseRunner, load_expression_data, save_network

logger = logging.getLogger(__name__)


class GenericGRNRunner(BaseRunner):
    """Generic GRN inference runner."""

    def __init__(self):
        """Initialize generic runner."""
        super().__init__("generic")

    def run(
        self,
        input_file: str,
        output_file: str,
        parameters: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """Run generic GRN inference."""
        try:
            # Validate input
            if not self.validate_input(input_file):
                raise RuntimeError("Input validation failed")

            # Load data
            data = load_expression_data(input_file)
            if data is None:
                raise RuntimeError("Failed to load expression data")

            self.logger.info(f"Loaded data: {data.shape}")

            # Run inference (basic correlation)
            network = self._infer_network(data, parameters)

            # Save output
            if not save_network(network, output_file):
                raise RuntimeError("Failed to save network")

            # Validate output
            if not self.validate_output(output_file):
                raise RuntimeError("Output validation failed")

            return {
                "status": "completed",
                "output_file": output_file,
                "metrics": {
                    "num_edges": len(network),
                    "num_genes": len(set(network[0]) | set(network[1])),
                },
            }

        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            raise

    def _infer_network(
        self,
        data: pd.DataFrame,
        parameters: Dict[str, Any],
    ) -> pd.DataFrame:
        """Infer GRN using correlation."""
        from app.services.runners.utils import compute_correlation

        correlation = compute_correlation(data)

        # Get threshold
        threshold = parameters.get("correlation_threshold", 0.5)

        # Extract edges
        edges = []
        for i in range(len(correlation)):
            for j in range(i + 1, len(correlation)):
                corr_value = abs(correlation.iloc[i, j])
                if corr_value >= threshold:
                    edges.append([
                        correlation.index[i],
                        correlation.columns[j],
                        corr_value,
                    ])

        return pd.DataFrame(edges, columns=["TF", "Target", "Score"])


# Convenience function for running
async def run_generic(
    input_file: str,
    output_file: str,
    parameters: Dict[str, Any],
) -> Dict[str, Any]:
    """Run generic GRN inference."""
    runner = GenericGRNRunner()
    return runner.run(input_file, output_file, parameters)
