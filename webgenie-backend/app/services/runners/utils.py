"""
Generic runner template and utilities for algorithm execution.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd


logger = logging.getLogger(__name__)


class BaseRunner:
    """Base class for algorithm runners."""

    def __init__(self, algorithm_name: str):
        """Initialize runner."""
        self.algorithm_name = algorithm_name
        self.logger = logging.getLogger(f"runners.{algorithm_name.lower()}")

    def run(
        self,
        input_file: str,
        output_file: str,
        parameters: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """Run algorithm. Must be implemented by subclasses."""
        raise NotImplementedError

    def validate_input(self, input_file: str) -> bool:
        """Validate input file."""
        try:
            if not Path(input_file).exists():
                self.logger.error(f"Input file not found: {input_file}")
                return False

            df = pd.read_csv(input_file)
            if df.empty:
                self.logger.error("Input file is empty")
                return False

            self.logger.info(f"Input validation passed: {input_file}")
            return True

        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return False

    def validate_output(self, output_file: str) -> bool:
        """Validate output file."""
        try:
            if not Path(output_file).exists():
                self.logger.error(f"Output file not found: {output_file}")
                return False

            df = pd.read_csv(output_file, sep="\t", header=None)
            if df.empty:
                self.logger.error("Output file is empty")
                return False

            self.logger.info(f"Output validation passed: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Output validation failed: {str(e)}")
            return False

    def parse_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate algorithm parameters."""
        return parameters

    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for algorithm."""
        return {}


def load_expression_data(file_path: str) -> Optional[pd.DataFrame]:
    """Load expression data from file."""
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path, index_col=0)
        elif file_path.endswith(".tsv"):
            return pd.read_csv(file_path, sep="\t", index_col=0)
        elif file_path.endswith(".h5ad"):
            try:
                import anndata
                adata = anndata.read_h5ad(file_path)
                return pd.DataFrame(
                    adata.X.T,
                    index=adata.var_names,
                    columns=adata.obs_names,
                )
            except ImportError:
                logger.error("anndata not installed, cannot read h5ad files")
                return None
        else:
            logger.warning(f"Unknown file format: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Failed to load expression data: {str(e)}")
        return None


def save_network(
    network_df: pd.DataFrame,
    output_file: str,
    format: str = "tsv",
) -> bool:
    """Save network to file."""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "tsv":
            network_df.to_csv(
                output_file,
                sep="\t",
                index=False,
                header=False,
            )
        elif format == "csv":
            network_df.to_csv(output_file, index=False)
        else:
            logger.warning(f"Unknown format: {format}, using TSV")
            network_df.to_csv(
                output_file,
                sep="\t",
                index=False,
                header=False,
            )

        logger.info(f"Network saved: {output_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to save network: {str(e)}")
        return False


def compute_correlation(data: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson correlation matrix."""
    return data.T.corr()


def compute_mutual_information(data: pd.DataFrame) -> pd.DataFrame:
    """Compute mutual information matrix."""
    from sklearn.preprocessing import scale
    from scipy.stats import entropy
    import numpy as np

    n_genes = data.shape[0]
    mi_matrix = np.zeros((n_genes, n_genes))

    scaled_data = scale(data.T, axis=0).T

    for i in range(n_genes):
        for j in range(i + 1, n_genes):
            gene_i = scaled_data[i]
            gene_j = scaled_data[j]

            # Digitize to 10 bins
            digitized_i = np.digitize(gene_i, np.linspace(-3, 3, 10))
            digitized_j = np.digitize(gene_j, np.linspace(-3, 3, 10))

            # Compute MI
            pxy = np.histogram2d(digitized_i, digitized_j, bins=10)[0] / len(gene_i)
            px = np.histogram(digitized_i, bins=10)[0] / len(gene_i)
            py = np.histogram(digitized_j, bins=10)[0] / len(gene_j)

            px_py = np.outer(px, py)
            nz = pxy > 0

            mi = np.sum(pxy[nz] * np.log(pxy[nz] / (px_py[nz] + 1e-10)))
            mi_matrix[i, j] = mi
            mi_matrix[j, i] = mi

    return pd.DataFrame(mi_matrix)
