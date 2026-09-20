from fastapi.testclient import TestClient

from claims_platform.api import app
from claims_platform.data import generate_claims, validate_claims
from claims_platform.model import train_models


def setup_module():
    train_models()


def test_generated_data_passes_quality_checks():
    assert validate_claims(generate_claims(100)) == []


def test_health_endpoint():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_prediction_rejects_invalid_claim():
    with TestClient(app) as client:
        response = client.post("/predict", json={"claim_amount": -1})
        assert response.status_code == 422
