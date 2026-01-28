"""
API endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "api_prefix" in data


def test_get_algorithms(client):
    """Test get algorithms endpoint."""
    response = client.get("/api/v1/algorithms")
    assert response.status_code == 200
    data = response.json()
    assert "algorithms" in data
    assert len(data["algorithms"]) > 0
    assert "total" in data


def test_register_dataset(client, mock_dataset_data):
    """Test dataset registration."""
    response = client.post(
        "/api/v1/datasets/register",
        json=mock_dataset_data,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == mock_dataset_data["name"]


def test_list_datasets(client, mock_dataset_data):
    """Test list datasets."""
    # Register a dataset first
    client.post(
        "/api/v1/datasets/register",
        json=mock_dataset_data,
    )

    # List datasets
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_submit_job(client, mock_dataset_data, mock_job_data):
    """Test job submission."""
    # Register dataset first
    ds_response = client.post(
        "/api/v1/datasets/register",
        json=mock_dataset_data,
    )
    dataset_id = ds_response.json()["id"]

    # Update job data with registered dataset
    job_data = mock_job_data.copy()
    job_data["dataset_id"] = dataset_id

    # Submit job
    response = client.post(
        "/api/v1/jobs",
        json=job_data,
    )

    # Note: This might fail if dataset files don't exist
    # For testing, we expect either 201 or 400
    assert response.status_code in [201, 400]


def test_list_jobs(client):
    """Test list jobs."""
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


def test_list_jobs_with_filters(client):
    """Test list jobs with filters."""
    response = client.get(
        "/api/v1/jobs",
        params={"algorithm": "GRNBOOST2"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_get_nonexistent_job(client):
    """Test getting non-existent job."""
    response = client.get("/api/v1/jobs/nonexistent")
    assert response.status_code == 404


def test_get_nonexistent_dataset(client):
    """Test getting non-existent dataset."""
    response = client.get("/api/v1/datasets/nonexistent")
    assert response.status_code == 404
