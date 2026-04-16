from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_batch_analyze_runs_and_persists_status():
    client = TestClient(app)

    async def fake_analyze_url(url: str, options: dict):
        return (
            {
                "url": url,
                "title": "T",
                "description": "D",
                "logo": None,
                "favicon": None,
                "emails": [],
                "phones": [],
                "socials": {},
                "tech_stack": [],
                "industry_guess": None,
                "language": None,
                "country_guess": None,
                "keywords": [],
                "schema_org": None,
                "og_tags": None,
                "screenshot_url": None,
                "page_speed_score": 100,
                "ai_summary": None,
                "timestamp": 0,
                "processing_time_ms": 0,
            },
            0,
        )

    with patch("app.tasks.batch_tasks.analyze_url", new=fake_analyze_url):
        resp = client.post(
            "/api/v1/batch-analyze/",
            json={"urls": ["https://example.com", "https://example.org"], "options": {}},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        batch_id = body["data"]["batch_id"]

        status_resp = client.get(f"/api/v1/batch-analyze/{batch_id}")
        assert status_resp.status_code == 200
        status_body = status_resp.json()
        assert status_body["success"] is True
        assert status_body["data"]["status"] in {"completed", "processing", "queued"}

        # Because Celery is eager under pytest, the batch should complete immediately.
        assert status_body["data"]["status"] == "completed"
        assert status_body["data"]["completed_count"] == 2
        assert status_body["data"]["failed_count"] == 0
        assert status_body["data"]["total_count"] == 2
        assert len(status_body["data"]["results"]) == 2

