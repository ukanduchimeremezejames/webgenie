"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import json

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_dataset(temp_data_dir):
    """Create sample dataset."""
    import pandas as pd

    data = {
        "Gene1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "Gene2": [5.0, 4.0, 3.0, 2.0, 1.0],
        "Gene3": [2.0, 2.0, 2.0, 2.0, 2.0],
    }
    df = pd.DataFrame(data, index=[f"Cell{i}" for i in range(5)])

    file_path = temp_data_dir / "sample.csv"
    df.to_csv(file_path)

    return {
        "id": "sample-001",
        "name": "Sample Dataset",
        "file_path": str(file_path),
        "df": df,
    }


@pytest.fixture
def sample_network(temp_data_dir):
    """Create sample network file."""
    network_data = [
        ["Gene1", "Gene2", "0.8"],
        ["Gene2", "Gene3", "0.6"],
        ["Gene3", "Gene1", "0.7"],
    ]

    file_path = temp_data_dir / "network.tsv"
    import pandas as pd

    df = pd.DataFrame(network_data, columns=["TF", "Target", "Score"])
    df.to_csv(file_path, sep="\t", index=False, header=False)

    return {
        "id": "result-001",
        "file_path": str(file_path),
        "df": df,
    }


@pytest.fixture
def mock_job_data():
    """Mock job data."""
    return {
        "dataset_id": "test-dataset-001",
        "algorithm": "GRNBOOST2",
        "parameters": {"alpha": 0.5},
        "name": "Test Job",
        "description": "Test job description",
    }


@pytest.fixture
def mock_dataset_data():
    """Mock dataset data."""
    return {
        "name": "Test Dataset",
        "description": "Test dataset",
        "species": "Human",
        "tissue": "Liver",
        "source": {
            "source_type": "local",
            "url": "s3://bucket/dataset.csv",
            "metadata": {},
        },
        "schema": {
            "gene_column": "Gene",
            "cell_column": "Cell",
            "expression_column": "Expression",
        },
    }
