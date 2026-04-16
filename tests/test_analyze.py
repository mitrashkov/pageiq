from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app


class TestAnalyzeEndpoint:
    def test_analyze_basic_smoke(self):
        client = TestClient(app)

        with patch("app.services.fetcher.html_fetcher.fetch_html") as mock_fetch_html, patch(
            "app.services.fetcher.html_fetcher.parse_html"
        ) as mock_parse_html:
            mock_fetch_html.return_value = ("<html><body>Test</body></html>", None, {})
            mock_parse_html.return_value = Mock()

            resp = client.post("/api/v1/analyze", json={"url": "https://example.com", "options": {}})
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert body["data"]["url"] == "https://example.com"