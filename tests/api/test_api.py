"""Tests for the FastAPI application."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_customer():
    """Load sample customer data."""
    sample_path = (
        Path(__file__).parent.parent.parent / "examples" / "sample_customer.json"
    )
    with open(sample_path) as f:
        return json.load(f)


@pytest.fixture
def sample_batch():
    """Load sample batch data."""
    sample_path = Path(__file__).parent.parent.parent / "examples" / "sample_batch.json"
    with open(sample_path) as f:
        return json.load(f)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert data["status"] in ["healthy", "degraded"]


@pytest.mark.skipif(
    not Path(__file__).parent.parent.parent.joinpath("mlruns").exists(),
    reason="Model not loaded - skipping prediction tests",
)
def test_predict_single(client, sample_customer):
    """Test single prediction endpoint."""
    response = client.post("/predict/single", json=sample_customer)

    # If model not loaded, should return 503
    if response.status_code == 503:
        pytest.skip("Model not loaded")

    assert response.status_code == 200
    data = response.json()

    assert "churn_probability" in data
    assert "will_churn" in data
    assert "risk_level" in data
    assert 0.0 <= data["churn_probability"] <= 1.0
    assert isinstance(data["will_churn"], bool)
    assert data["risk_level"] in ["low", "medium", "high"]


@pytest.mark.skipif(
    not Path(__file__).parent.parent.parent.joinpath("mlruns").exists(),
    reason="Model not loaded - skipping prediction tests",
)
def test_predict_batch(client, sample_batch):
    """Test batch prediction endpoint."""
    response = client.post("/predict", json=sample_batch)

    # If model not loaded, should return 503
    if response.status_code == 503:
        pytest.skip("Model not loaded")

    assert response.status_code == 200
    data = response.json()

    assert "predictions" in data
    assert "model_version" in data
    assert "total_customers" in data
    assert len(data["predictions"]) == len(sample_batch["customers"])

    for pred in data["predictions"]:
        assert "churn_probability" in pred
        assert "will_churn" in pred
        assert "risk_level" in pred
        assert 0.0 <= pred["churn_probability"] <= 1.0


def test_predict_single_validation_error(client):
    """Test single prediction with invalid data."""
    invalid_data = {
        "gender": "Invalid",  # Invalid gender
        "is_senior_citizen": "not_a_bool",  # Invalid type
    }

    response = client.post("/predict/single", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_predict_batch_empty(client):
    """Test batch prediction with empty list."""
    response = client.post("/predict", json={"customers": []})
    assert response.status_code == 422  # Validation error


def test_openapi_docs(client):
    """Test that OpenAPI docs are available."""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    assert "paths" in openapi
    assert "/health" in openapi["paths"]
    assert "/predict" in openapi["paths"]
    assert "/predict/single" in openapi["paths"]
