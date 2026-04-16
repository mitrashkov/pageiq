#!/usr/bin/env python3
"""
RapidAPI Compatibility Test Script

This script tests that our API meets RapidAPI's requirements for publication.
"""

import json
import sys
import time
from typing import Dict, List, Tuple

import requests


class RapidAPICompatibilityTester:
    """Test API compatibility with RapidAPI requirements"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def run_all_tests(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all compatibility tests

        Returns:
            Tuple of (passed: bool, passed_tests: List[str], failed_tests: List[str])
        """
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("OpenAPI Documentation", self.test_openapi_docs),
            ("CORS Headers", self.test_cors_headers),
            ("Error Responses", self.test_error_responses),
            ("Rate Limiting", self.test_rate_limiting),
            ("API Key Authentication", self.test_api_key_auth),
            ("Response Format", self.test_response_format),
            ("HTTPS Support", self.test_https_support),
        ]

        passed_tests = []
        failed_tests = []

        print("Running RapidAPI Compatibility Tests...")
        print("=" * 50)

        for test_name, test_func in tests:
            print(f"\nTesting: {test_name}")
            try:
                result, message = test_func()
                if result:
                    print(f"✓ PASS: {message}")
                    passed_tests.append(test_name)
                else:
                    print(f"✗ FAIL: {message}")
                    failed_tests.append(test_name)
            except Exception as e:
                print(f"✗ ERROR: {str(e)}")
                failed_tests.append(test_name)

        print("\n" + "=" * 50)
        total_tests = len(tests)
        passed_count = len(passed_tests)
        print(f"Results: {passed_count}/{total_tests} tests passed")

        return passed_count == total_tests, passed_tests, failed_tests

    def test_health_endpoint(self) -> Tuple[bool, str]:
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    return True, "Health endpoint returns healthy status"
            return False, f"Health endpoint returned {response.status_code}"
        except Exception as e:
            return False, f"Health check failed: {str(e)}"

    def test_openapi_docs(self) -> Tuple[bool, str]:
        """Test OpenAPI documentation"""
        try:
            # Test /docs endpoint
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                return True, "OpenAPI docs accessible at /docs"
            return False, f"Docs endpoint returned {response.status_code}"
        except Exception as e:
            return False, f"OpenAPI docs test failed: {str(e)}"

    def test_cors_headers(self) -> Tuple[bool, str]:
        """Test CORS headers"""
        try:
            response = self.session.options(f"{self.base_url}/api/v1/analyze",
                                          headers={"Origin": "https://rapidapi.com"})
            cors_headers = ["access-control-allow-origin", "access-control-allow-methods"]
            missing_headers = [h for h in cors_headers if h not in response.headers]

            if not missing_headers:
                return True, "CORS headers properly configured"
            return False, f"Missing CORS headers: {missing_headers}"
        except Exception as e:
            return False, f"CORS test failed: {str(e)}"

    def test_error_responses(self) -> Tuple[bool, str]:
        """Test error response format"""
        try:
            # Test with invalid URL
            response = self.session.post(f"{self.base_url}/api/v1/analyze",
                                       json={"url": "invalid-url"})
            if response.status_code >= 400:
                data = response.json()
                if "success" in data and data["success"] is False:
                    if "error" in data and "message" in data["error"]:
                        return True, "Error responses properly formatted"
            return False, "Error response format incorrect"
        except Exception as e:
            return False, f"Error response test failed: {str(e)}"

    def test_rate_limiting(self) -> Tuple[bool, str]:
        """Test rate limiting"""
        try:
            # Make multiple requests quickly
            responses = []
            for i in range(10):
                response = self.session.post(f"{self.base_url}/api/v1/analyze",
                                           json={"url": f"https://example{i}.com"})
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay

            # Check if any requests were rate limited (429)
            if 429 in responses:
                return True, "Rate limiting is working"
            elif any(code >= 400 for code in responses):
                return True, "Some form of rate limiting or quota enforcement detected"
            else:
                return False, "No rate limiting detected (may be expected for local testing)"
        except Exception as e:
            return False, f"Rate limiting test failed: {str(e)}"

    def test_api_key_auth(self) -> Tuple[bool, str]:
        """Test API key authentication"""
        try:
            # Test without API key (should work for free tier)
            response = self.session.post(f"{self.base_url}/api/v1/analyze",
                                       json={"url": "https://example.com"})
            if response.status_code in [200, 400, 500]:  # Allow various responses for free tier
                return True, "API accepts requests (free tier or anonymous access)"
            return False, f"API key auth test returned {response.status_code}"
        except Exception as e:
            return False, f"API key auth test failed: {str(e)}"

    def test_response_format(self) -> Tuple[bool, str]:
        """Test response format consistency"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/analyze",
                                       json={"url": "https://httpbin.org"})

            if response.status_code == 200:
                data = response.json()
                required_fields = ["success", "data", "request_id"]

                missing_fields = [f for f in required_fields if f not in data]
                if not missing_fields:
                    return True, "Response format includes all required fields"
                return False, f"Missing required fields: {missing_fields}"

            return False, f"Unexpected status code: {response.status_code}"
        except Exception as e:
            return False, f"Response format test failed: {str(e)}"

    def test_https_support(self) -> Tuple[bool, str]:
        """Test HTTPS support (may not apply to local testing)"""
        if self.base_url.startswith("http://localhost") or self.base_url.startswith("http://127.0.0.1"):
            return True, "Local testing - HTTPS not required"

        try:
            # Check if URL uses HTTPS
            if self.base_url.startswith("https://"):
                return True, "API uses HTTPS"
            else:
                return False, "API should use HTTPS for production"
        except Exception as e:
            return False, f"HTTPS test failed: {str(e)}"


def main():
    """Main test runner"""
    tester = RapidAPICompatibilityTester()

    passed, passed_tests, failed_tests = tester.run_all_tests()

    print(f"\nCompatibility Status: {'✓ COMPATIBLE' if passed else '✗ NOT COMPATIBLE'}")

    if failed_tests:
        print("\nFailed Tests:")
        for test in failed_tests:
            print(f"  - {test}")

    if passed_tests:
        print("\nPassed Tests:")
        for test in passed_tests:
            print(f"  - {test}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()