from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_extract_schema_allows_missing_og_tags_without_500():
    mock_html = "<html><head></head><body><h1>No OG tags</h1></body></html>"

    with patch("app.api.v1.endpoints.extract.robots_checker.can_fetch", return_value=True):
        with patch(
            "app.api.v1.endpoints.extract.html_fetcher.fetch_html_async",
            return_value=(mock_html, None, {}),
        ):
            with patch("app.api.v1.endpoints.extract.extract_schema_org", return_value={"@type": "WebSite"}):
                with patch("app.api.v1.endpoints.extract.extract_open_graph", return_value=None):
                    response = client.post("/api/v1/extract/schema", json={"url": "https://example.com"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_org"]["@type"] == "WebSite"
    assert "og_tags" in payload
    assert payload["og_tags"] is None


def test_tech_detection_returns_languages_and_combined_technologies():
    mock_html = """
    <html>
      <head>
        <link rel="stylesheet" href="/styles.css">
      </head>
      <body>
        <div id="app"></div>
        <script src="/static/js/react.js"></script>
      </body>
    </html>
    """

    with patch(
        "app.api.v1.endpoints.analyze.html_fetcher.fetch_html_async",
        return_value=(mock_html, None, {}),
    ):
        response = client.post("/api/v1/analyze/tech", json={"url": "https://example.com", "options": {}})

    assert response.status_code == 200
    payload = response.json()

    assert "languages" in payload
    assert "HTML" in payload["languages"]
    assert "CSS" in payload["languages"]
    assert "JavaScript" in payload["languages"]

    assert "technologies" in payload
    assert "HTML" in payload["technologies"]
    assert "React" in payload["technologies"]
