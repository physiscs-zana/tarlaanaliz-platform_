from fastapi.testclient import TestClient

from src.presentation.api.main import create_app


def test_create_app_importable() -> None:
    app = create_app()
    assert app is not None


def test_health_endpoint_returns_200() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_correlation_header_exists() -> None:
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Correlation-Id" in response.headers
    assert response.headers["X-Correlation-Id"]
