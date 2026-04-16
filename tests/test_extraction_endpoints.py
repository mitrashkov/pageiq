"""
Comprehensive tests for extraction endpoints - Week 8 coverage.
"""
import pytest
from unittest.mock import patch, Mock, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestExtractEmailsEndpoint:
    """Tests for email extraction endpoint"""
    
    def test_extract_emails_success(self):
        """Test successful email extraction"""
        mock_html = """
        <html>
            <head><title>Contact</title></head>
            <body>
                <a href="mailto:info@example.com">Email us</a>
                <p>Support: support@example.com</p>
            </body>
        </html>
        """
        
        with patch('app.api.v1.endpoints.extract.robots_checker.can_fetch', return_value=True):
            with patch('app.api.v1.endpoints.extract.html_fetcher.fetch_html', return_value=(mock_html, None, {})):
                with patch('app.api.v1.endpoints.extract.html_fetcher.parse_html'):
                    with patch('app.api.v1.endpoints.extract.extract_emails_service', return_value=['info@example.com', 'support@example.com']):
                        response = client.post(
                            "/api/v1/extract/emails",
                            json={"url": "https://example.com"}
                        )
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert data["url"] == "https://example.com"
                        assert len(data["emails"]) == 2
                        assert data["count"] == 2
    
    def test_extract_emails_robots_blocked(self):
        """Test email extraction blocked by robots.txt"""
        with patch('app.api.v1.endpoints.extract.robots_checker.can_fetch', return_value=False):
            response = client.post(
                "/api/v1/extract/emails",
                json={"url": "https://example.com"}
            )
            
            assert response.status_code == 403
    
    def test_extract_emails_fetch_error(self):
        """Test email extraction with fetch error"""
        with patch('app.api.v1.endpoints.extract.robots_checker.can_fetch', return_value=True):
            with patch('app.api.v1.endpoints.extract.html_fetcher.fetch_html', return_value=(None, "Fetch error", {})):
                response = client.post(
                    "/api/v1/extract/emails",
                    json={"url": "https://example.com"}
                )
                
                assert response.status_code == 400
    
    def test_extract_emails_invalid_url(self):
        """Test email extraction with invalid URL"""
        response = client.post(
            "/api/v1/extract/emails",
            json={"url": "not a url"}
        )
        
        assert response.status_code == 422  # Validation error


class TestExtractSchemaEndpoint:
    """Tests for schema extraction endpoint"""
    
    def test_extract_schema_success(self):
        """Test successful schema extraction"""
        mock_schema = {"@type": "Organization", "name": "Example Corp"}
        mock_og = {"title": "Example", "description": "Test"}
        
        with patch('app.api.v1.endpoints.extract.robots_checker.can_fetch', return_value=True):
            with patch('app.api.v1.endpoints.extract.html_fetcher.fetch_html', return_value=("<html></html>", None, {})):
                with patch('app.api.v1.endpoints.extract.html_fetcher.parse_html'):
                    with patch('app.api.v1.endpoints.extract.extract_schema_org', return_value=mock_schema):
                        with patch('app.api.v1.endpoints.extract.extract_open_graph', return_value=mock_og):
                            response = client.post(
                                "/api/v1/extract/schema",
                                json={"url": "https://example.com"}
                            )
                            
                            assert response.status_code == 200
                            data = response.json()
                            assert data["schema_org"]["@type"] == "Organization"
                            assert data["og_tags"]["title"] == "Example"
    
    def test_extract_schema_robots_blocked(self):
        """Test schema extraction blocked by robots.txt"""
        with patch('app.api.v1.endpoints.extract.robots_checker.can_fetch', return_value=False):
            response = client.post(
                "/api/v1/extract/schema",
                json={"url": "https://example.com"}
            )
            
            assert response.status_code == 403


class TestMetadataExtractEndpoint:
    """Tests for metadata extraction endpoint"""
    
    def test_extract_metadata_success(self):
        """Test successful metadata extraction"""
        with patch('app.api.v1.endpoints.extract.robots_checker.can_fetch', return_value=True):
            with patch('app.api.v1.endpoints.extract.html_fetcher.fetch_html', return_value=("<html></html>", None, {})):
                with patch('app.api.v1.endpoints.extract.html_fetcher.parse_html'):
                    with patch('app.api.v1.endpoints.extract.extract_title', return_value="Test Title"):
                        with patch('app.api.v1.endpoints.extract.extract_description', return_value="Test Description"):
                            with patch('app.api.v1.endpoints.extract.extract_schema_org', return_value=None):
                                with patch('app.api.v1.endpoints.extract.extract_open_graph', return_value=None):
                                    response = client.post(
                                        "/api/v1/extract/metadata",
                                        json={"url": "https://example.com"}
                                    )
                                    
                                    assert response.status_code == 200
                                    data = response.json()
                                    assert data["title"] == "Test Title"
                                    assert data["description"] == "Test Description"
    
    def test_extract_metadata_parse_error(self):
        """Test metadata extraction with parse error"""
        with patch('app.api.v1.endpoints.extract.robots_checker.can_fetch', return_value=True):
            with patch('app.api.v1.endpoints.extract.html_fetcher.fetch_html', return_value=("<html></html>", None, {})):
                with patch('app.api.v1.endpoints.extract.html_fetcher.parse_html', return_value=None):
                    response = client.post(
                        "/api/v1/extract/metadata",
                        json={"url": "https://example.com"}
                    )
                    
                    assert response.status_code == 400


class TestSEOAuditEndpoint:
    """Tests for SEO audit endpoint"""
    
    def test_seo_audit_success(self):
        """Test successful SEO audit"""
        from bs4 import BeautifulSoup
        
        mock_html = """
        <html>
            <head>
                <meta name="viewport" content="width=device-width">
                <meta name="description" content="Test description for SEO purposes">
                <title>Test Title</title>
            </head>
            <body>
                <h1>Main Heading</h1>
                <img src="test.jpg" alt="Test image">
            </body>
        </html>
        """
        
        with patch('app.api.v1.endpoints.seo.robots_checker.can_fetch', return_value=True):
            with patch('app.api.v1.endpoints.seo.html_fetcher.fetch_html', return_value=(mock_html, None, {})):
                with patch('app.api.v1.endpoints.seo.html_fetcher.parse_html', return_value=BeautifulSoup(mock_html, 'html.parser')):
                    response = client.post(
                        "/api/v1/seo/seo-audit",
                        json={"url": "https://example.com"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "score" in data
                    assert 0 <= data["score"] <= 100
                    assert len(data["audit_items"]) > 0
    
    def test_seo_audit_robots_blocked(self):
        """Test SEO audit blocked by robots.txt"""
        with patch('app.api.v1.endpoints.seo.robots_checker.can_fetch', return_value=False):
            response = client.post(
                "/api/v1/seo/seo-audit",
                json={"url": "https://example.com"}
            )
            
            assert response.status_code == 403


class TestBrokenLinksEndpoint:
    """Tests for broken links detection endpoint"""
    
    def test_broken_links_success(self):
        """Test successful broken links detection"""
        from bs4 import BeautifulSoup
        
        mock_html = """
        <html>
            <body>
                <a href="https://example.com/page1">Internal Link 1</a>
                <a href="https://example.com/page2">Internal Link 2</a>
                <a href="https://external.com">External Link</a>
                <a href="#anchor">Anchor Link</a>
            </body>
        </html>
        """
        
        with patch('app.api.v1.endpoints.seo.robots_checker.can_fetch', return_value=True):
            with patch('app.api.v1.endpoints.seo.html_fetcher.fetch_html', return_value=(mock_html, None, {})):
                with patch('app.api.v1.endpoints.seo.html_fetcher.parse_html', return_value=BeautifulSoup(mock_html, 'html.parser')):
                    response = client.post(
                        "/api/v1/seo/broken-links",
                        json={"url": "https://example.com", "check_external": False}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["url"] == "https://example.com"
                    assert data["total_links"] >= 3
                    assert data["internal_links"] >= 2
                    assert data["external_links"] >= 1
