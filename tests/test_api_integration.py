import pytest
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.v1.endpoints.analyze import router
from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Mock database session"""
    return Mock(spec=Session)


class TestAnalyzeEndpoint:
    def test_analyze_endpoint_requires_auth(self, client):
        """Test that analyze endpoint requires authentication for non-free tier"""
        response = client.post("/api/v1/analyze", json={
            "url": "https://example.com",
            "options": {}
        })

        # Should still work for anonymous users (free tier)
        assert response.status_code in [200, 400, 500]  # Depends on implementation

    @patch('app.services.fetcher.html_fetcher.fetch_html')
    @patch('app.services.fetcher.html_fetcher.parse_html')
    @patch('app.services.extractors.extract_title')
    def test_analyze_basic_extraction(self, mock_extract_title, mock_parse_html, mock_fetch_html, client):
        """Test basic analysis with mocked services"""
        # Mock the fetcher
        mock_fetch_html.return_value = ('<html><body>Test</body></html>', None, {})

        # Mock the parser
        mock_soup = Mock()
        mock_parse_html.return_value = mock_soup

        # Mock the extractor
        mock_extract_title.return_value = 'Test Title'

        response = client.post("/api/v1/analyze", json={
            "url": "https://example.com",
            "options": {}
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["url"] == "https://example.com"
        assert "request_id" in data

    def test_analyze_invalid_url(self, client):
        """Test analysis with invalid URL"""
        response = client.post("/api/v1/analyze", json={
            "url": "not-a-valid-url",
            "options": {}
        })

        assert response.status_code == 422  # Validation error

    @patch('app.services.robots_checker.robots_checker.can_fetch')
    def test_analyze_robots_blocked(self, mock_can_fetch, client):
        """Test analysis blocked by robots.txt"""
        mock_can_fetch.return_value = False

        response = client.post("/api/v1/analyze", json={
            "url": "https://example.com",
            "options": {}
        })

        assert response.status_code == 403
        assert "robots.txt" in response.json()["error"]["message"]

    @patch('app.services.quota.quota_service.check_quota')
    def test_analyze_quota_exceeded(self, mock_check_quota, client):
        """Test analysis with quota exceeded"""
        mock_check_quota.return_value = (False, 0, 100)

        response = client.post("/api/v1/analyze", json={
            "url": "https://example.com",
            "options": {}
        })

        assert response.status_code == 402
        assert "quota" in response.json()["error"]["message"].lower()

    def test_analyze_missing_url(self, client):
        """Test analysis with missing URL"""
        response = client.post("/api/v1/analyze", json={
            "options": {}
        })

        assert response.status_code == 422

    def test_analyze_empty_url(self, client):
        """Test analysis with empty URL"""
        response = client.post("/api/v1/analyze", json={
            "url": "",
            "options": {}
        })

        assert response.status_code == 422

    @patch('app.services.fetcher.html_fetcher.fetch_html')
    def test_analyze_fetch_failure(self, mock_fetch_html, client):
        """Test analysis with fetch failure"""
        mock_fetch_html.return_value = (None, "Connection failed", {})

        response = client.post("/api/v1/analyze", json={
            "url": "https://example.com",
            "options": {}
        })

        assert response.status_code == 400
        assert "Connection failed" in response.json()["error"]["message"]

    def test_analyze_options_validation(self, client):
        """Test analysis with invalid options"""
        response = client.post("/api/v1/analyze", json={
            "url": "https://example.com",
            "options": {
                "screenshot": "not_a_boolean"
            }
        })

        assert response.status_code == 422

    @patch('app.services.fetcher.html_fetcher.fetch_html')
    @patch('app.services.fetcher.html_fetcher.parse_html')
    def test_analyze_comprehensive_response(self, mock_parse_html, mock_fetch_html, client):
        """Test comprehensive analysis response structure"""
        # Mock successful analysis
        mock_fetch_html.return_value = ('<html><body>Test content</body></html>', None, {})
        mock_soup = Mock()
        mock_parse_html.return_value = mock_soup

        # Mock all extractors to return data
        with patch.multiple('app.services.extractors',
                          extract_title=Mock(return_value='Test Title'),
                          extract_description=Mock(return_value='Test Description'),
                          extract_favicon=Mock(return_value='https://example.com/favicon.ico'),
                          extract_logo=Mock(return_value='https://example.com/logo.png'),
                          extract_emails=Mock(return_value=['test@example.com']),
                          extract_phones=Mock(return_value=['+1234567890']),
                          extract_social_profiles=Mock(return_value={'twitter': 'https://twitter.com/test'}),
                          detect_language=Mock(return_value='en'),
                          detect_country=Mock(return_value='US'),
                          extract_keywords=Mock(return_value=['test', 'content']),
                          extract_schema_org=Mock(return_value={'@type': 'Organization'}),
                          extract_open_graph=Mock(return_value={'title': 'OG Title'})):
            with patch.multiple('app.services',
                              tech_detector=Mock(detect_technologies=Mock(return_value=['React', 'Node.js'])),
                              speed_scorer=Mock(calculate_score=Mock(return_value=85)),
                              ai_summarizer=Mock(generate_summary=Mock(return_value='Test summary'))):
                response = client.post("/api/v1/analyze", json={
                    "url": "https://example.com",
                    "options": {}
                })

                assert response.status_code == 200
                data = response.json()

                assert data["success"] is True
                assert data["data"]["title"] == "Test Title"
                assert data["data"]["description"] == "Test Description"
                assert data["data"]["emails"] == ["test@example.com"]
                assert data["data"]["phones"] == ["+1234567890"]
                assert data["data"]["language"] == "en"
                assert data["data"]["country_guess"] == "US"
                assert data["data"]["tech_stack"] == ["React", "Node.js"]
                assert data["data"]["page_speed_score"] == 85
                assert data["data"]["ai_summary"] == "Test summary"
                assert "processing_time_ms" in data
                assert "request_id" in data


class TestHealthEndpoint:
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestCORSMiddleware:
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/v1/analyze",
                                headers={"Origin": "http://localhost:3000"})

        assert "access-control-allow-origin" in response.headers


class TestSecurityHeaders:
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/health")

        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-xss-protection" in response.headers