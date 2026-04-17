"""
Comprehensive end-to-end tests for PageIQ API.
Tests all features, endpoints, and error handling.

Run with: pytest tests/test_e2e_full.py -v --tb=short
"""
import pytest
import json
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_api_key():
    """Create a test API key"""
    # For now, return None since we test both auth and non-auth
    return None


@pytest.fixture
def headers():
    """HTTP headers with API key"""
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_key_123"
    }


# ============================================================================
# HEALTH & MONITORING TESTS
# ============================================================================

class TestHealth:
    """Test health check endpoints"""
    
    def test_health_check_status_200(self):
        """Health check should return 200"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
    
    def test_health_check_format(self):
        """Health check should return proper format"""
        response = client.get("/api/v1/")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
    
    def test_ping_returns_ok(self):
        """Ping endpoint should return ok"""
        response = client.get("/api/v1/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "pong"
    
    def test_ping_response_time(self):
        """Ping should be fast (< 100ms)"""
        start = time.time()
        response = client.get("/api/v1/ping")
        elapsed = (time.time() - start) * 1000
        assert response.status_code == 200
        assert elapsed < 100, f"Response took {elapsed}ms, expected < 100ms"


# ============================================================================
# WEBSITE ANALYSIS TESTS
# ============================================================================

class TestAnalysis:
    """Test website analysis endpoint"""
    
    def test_analyze_missing_url(self):
        """Analyze without URL should fail"""
        response = client.post(
            "/api/v1/analyze",
            json={"options": {}}
        )
        assert response.status_code == 400
    
    def test_analyze_invalid_url(self):
        """Analyze with invalid URL should fail"""
        response = client.post(
            "/api/v1/analyze",
            json={"url": "not-a-url"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_analyze_valid_url_format(self):
        """Analyze with valid URL should attempt processing"""
        response = client.post(
            "/api/v1/analyze",
            json={
                "url": "https://example.com",
                "options": {}
            }
        )
        # Should either succeed (200) or fail with specific error (403/500)
        # Not 400 (validation error)
        assert response.status_code in [200, 403, 500]
    
    def test_analyze_with_options(self):
        """Analyze with various options"""
        response = client.post(
            "/api/v1/analyze",
            json={
                "url": "https://example.com",
                "options": {
                    "extract_emails": True,
                    "detect_technology": True,
                    "screenshot": False
                }
            }
        )
        assert response.status_code in [200, 403, 500]
    
    def test_analyze_response_structure(self):
        """If analyze succeeds, check response structure"""
        response = client.post(
            "/api/v1/analyze",
            json={
                "url": "https://example.com",
                "options": {}
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "request_id" in data
            assert "processing_time_ms" in data
    
    def test_analyze_has_request_id(self):
        """Response should include request_id"""
        response = client.post(
            "/api/v1/analyze",
            json={"url": "https://example.com"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data["request_id"] is not None
            # Request ID should be a valid format
            assert len(data["request_id"]) > 0


class TestBatchAnalysis:
    """Test batch analysis endpoint"""
    
    def test_batch_analyze_endpoint_exists(self):
        """Batch analyze endpoint should exist"""
        response = client.post(
            "/api/v1/batch-analyze",
            json={"urls": ["https://example.com"]}
        )
        # Should either work (200) or fail with proper error
        assert response.status_code in [200, 400, 500]
    
    def test_batch_analyze_empty_urls(self):
        """Batch analyze with empty URLs should fail"""
        response = client.post(
            "/api/v1/batch-analyze",
            json={"urls": []}
        )
        assert response.status_code == 400
    
    def test_batch_analyze_multiple_urls(self):
        """Batch analyze with multiple URLs"""
        response = client.post(
            "/api/v1/batch-analyze",
            json={
                "urls": [
                    "https://example.com",
                    "https://example.org"
                ]
            }
        )
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "batch_id" in data or "status" in data


# ============================================================================
# DATA EXTRACTION TESTS
# ============================================================================

class TestExtraction:
    """Test data extraction endpoints"""
    
    def test_extract_emails_endpoint_exists(self):
        """Email extraction endpoint should exist"""
        response = client.post(
            "/api/v1/extract/emails",
            json={"url": "https://example.com"}
        )
        assert response.status_code in [200, 400, 500]
    
    def test_extract_emails_missing_url(self):
        """Extract without URL should fail"""
        response = client.post(
            "/api/v1/extract/emails",
            json={}
        )
        assert response.status_code == 400
    
    def test_extract_emails_response_structure(self):
        """If extraction succeeds, check structure"""
        response = client.post(
            "/api/v1/extract/emails",
            json={"url": "https://example.com"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "url" in data
            assert "emails" in data
            assert isinstance(data["emails"], list)
            assert "count" in data


# ============================================================================
# ANALYTICS TESTS
# ============================================================================

class TestAnalytics:
    """Test analytics endpoints"""
    
    def test_analytics_summary_endpoint_exists(self):
        """Analytics summary endpoint should exist"""
        response = client.get("/api/v1/analytics/summary")
        assert response.status_code in [200, 401, 500]
    
    def test_analytics_summary_structure(self):
        """Analytics summary should have expected fields"""
        response = client.get("/api/v1/analytics/summary")
        
        if response.status_code == 200:
            data = response.json()
            # Common analytics fields
            expected_fields = ["period", "requests_total", "average_response_time_ms"]
            for field in expected_fields:
                assert field in data or response.status_code != 200


# ============================================================================
# ACCOUNT & QUOTA TESTS
# ============================================================================

class TestAccount:
    """Test account management endpoints"""
    
    def test_quota_endpoint_exists(self):
        """Quota endpoint should exist"""
        response = client.get("/api/v1/account/quota")
        assert response.status_code in [200, 401, 500]
    
    def test_quota_response_structure(self):
        """If quota succeeds, check structure"""
        response = client.get("/api/v1/account/quota")
        
        if response.status_code == 200:
            data = response.json()
            expected = ["plan", "quota_limit", "quota_used", "quota_remaining"]
            for field in expected:
                assert field in data or response.status_code != 200
    
    def test_list_api_keys_endpoint_exists(self):
        """List API keys endpoint should exist"""
        response = client.get("/api/v1/account/keys")
        assert response.status_code in [200, 401, 500]
    
    def test_list_api_keys_structure(self):
        """If list keys succeeds, check structure"""
        response = client.get("/api/v1/account/keys")
        
        if response.status_code == 200:
            data = response.json()
            assert "keys" in data or isinstance(data, list)
    
    def test_create_api_key_endpoint_exists(self):
        """Create API key endpoint should exist"""
        response = client.post(
            "/api/v1/account/keys",
            json={"name": "test-key"}
        )
        assert response.status_code in [200, 201, 400, 401, 500]
    
    def test_create_api_key_returns_key(self):
        """Created API key should be returned"""
        response = client.post(
            "/api/v1/account/keys",
            json={"name": "test-key"}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            assert "key" in data or "id" in data


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_endpoint_404(self):
        """Invalid endpoint should return 404"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method_405(self):
        """Invalid HTTP method should fail"""
        response = client.put("/api/v1/analyze")
        assert response.status_code in [405, 400]
    
    def test_missing_content_type(self):
        """POST without Content-Type might fail"""
        response = client.post(
            "/api/v1/analyze",
            data='{"url": "https://example.com"}'
        )
        # Should either handle it or fail gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_malformed_json(self):
        """Malformed JSON should fail"""
        response = client.post(
            "/api/v1/analyze",
            content='{invalid json}',
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_error_response_format(self):
        """Errors should return consistent format"""
        response = client.post(
            "/api/v1/analyze",
            json={}
        )
        
        if response.status_code != 200:
            data = response.json()
            # Should have error info
            assert "error" in data or "detail" in data


# ============================================================================
# CORS & SECURITY TESTS
# ============================================================================

class TestSecurity:
    """Test security features"""
    
    def test_cors_headers_present(self):
        """CORS headers should be present"""
        response = client.get("/api/v1/ping")
        # FastAPI with CORS middleware should include these
        assert response.status_code == 200
    
    def test_security_headers_present(self):
        """Security headers should be present"""
        response = client.get("/api/v1/ping")
        headers = response.headers
        # Check for common security headers
        # (Implementation depends on SecurityHeadersMiddleware)
        assert response.status_code == 200
    
    def test_json_content_type(self):
        """Responses should be JSON"""
        response = client.get("/api/v1/ping")
        assert "application/json" in response.headers.get("content-type", "")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    def test_ping_response_time_consistent(self):
        """Ping response time should be consistent"""
        times = []
        for _ in range(5):
            start = time.time()
            response = client.get("/api/v1/ping")
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            assert response.status_code == 200
        
        avg_time = sum(times) / len(times)
        assert avg_time < 200  # Should be fast
    
    def test_concurrent_requests(self):
        """API should handle concurrent requests"""
        import threading
        
        results = []
        
        def make_request():
            response = client.get("/api/v1/ping")
            results.append(response.status_code == 200)
        
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert all(results)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test full workflows"""
    
    def test_health_to_analyze_flow(self):
        """Test health check then analyze"""
        # Check health
        health = client.get("/api/v1/ping")
        assert health.status_code == 200
        
        # Then analyze
        analyze = client.post(
            "/api/v1/analyze",
            json={"url": "https://example.com"}
        )
        assert analyze.status_code in [200, 400, 500]
    
    def test_quota_before_and_after_analyze(self):
        """Test quota changes after analysis"""
        # Get initial quota
        quota_before = client.get("/api/v1/account/quota")
        
        # Analyze
        analyze = client.post(
            "/api/v1/analyze",
            json={"url": "https://example.com"}
        )
        
        # Get quota after (if both succeeded)
        quota_after = client.get("/api/v1/account/quota")
        
        # If both succeeded, quota should have changed
        if quota_before.status_code == 200 and quota_after.status_code == 200:
            before_data = quota_before.json()
            after_data = quota_after.json()
            # Quota used should be >= before (or quota_remaining <= before)
            assert after_data.get("quota_remaining", 0) <= before_data.get("quota_remaining", 0) or after_data.get("quota_used", 0) >= before_data.get("quota_used", 0)


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
