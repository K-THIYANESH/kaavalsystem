"""Smoke tests for the KAAVAL backend API."""

from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_health_endpoint() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"


def test_dashboard_metrics() -> None:
    response = client.get("/api/analytics/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert "average_match_latency_ms" in payload
    assert payload["active_jobs"] >= 0


def test_camera_start_request_payload() -> None:
    response = client.post(
        "/api/camera/start",
        json={"device_id": 0, "frame_skip": 3, "adaptive": True},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"initializing", "running", "idle"}


def test_database_search_requires_embedding() -> None:
    response = client.post("/api/database/search", json={"filters": {}})
    assert response.status_code == 422


def test_results_export_flow() -> None:
    response = client.get("/api/results/evidence_pack/example-job")
    assert response.status_code == 200
    payload = response.json()
    assert "compressed_bundle" in payload

