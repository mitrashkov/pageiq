from fastapi.testclient import TestClient

from app.main import app


def test_v1_health_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"


def test_analytics_endpoints_smoke():
    client = TestClient(app)

    resp = client.get("/api/v1/analytics/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "usage_stats" in body["data"]
    assert "popular_domains" in body["data"]
    assert "performance_metrics" in body["data"]

    resp2 = client.get("/api/v1/analytics/performance")
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["success"] is True
    assert "average_response_time_ms" in body2["data"]

    resp3 = client.get("/api/v1/analytics/endpoints")
    assert resp3.status_code == 200
    body3 = resp3.json()
    assert body3["success"] is True
    assert "endpoint_usage" in body3["data"]

