import time
from locust import HttpUser, task, between

class WebsiteAnalyzerUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def analyze_website(self):
        """Simulate website analysis requests"""
        test_urls = [
            "https://example.com",
            "https://httpbin.org",
            "https://jsonplaceholder.typicode.com",
            "https://github.com",
        ]

        for url in test_urls[:1]:  # Test with one URL for simplicity
            self.client.post("/api/v1/analyze", json={
                "url": url,
                "options": {}
            })

    @task(1)
    def health_check(self):
        """Simulate health check requests"""
        self.client.get("/health")

    @task(1)
    def metrics_check(self):
        """Simulate metrics requests"""
        self.client.get("/metrics")

    def on_start(self):
        """Setup before starting the test"""
        # Could add authentication setup here if needed
        pass