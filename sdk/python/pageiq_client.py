# PageIQ Python SDK

import requests
from typing import Dict, List, Optional, Union

class PageIQClient:
    """Python client for PageIQ API"""

    def __init__(self, api_key: str, base_url: str = "https://pageiq.p.rapidapi.com"):
        """
        Initialize the PageIQ client

        Args:
            api_key: Your RapidAPI key
            base_url: API base URL (default: RapidAPI endpoint)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': 'pageiq.p.rapidapi.com',
            'Content-Type': 'application/json'
        })

    def analyze_website(
        self,
        url: str,
        screenshot: bool = False,
        use_browser: bool = False
    ) -> Dict:
        """
        Analyze a single website

        Args:
            url: Website URL to analyze
            screenshot: Include screenshot (Pro plan required)
            use_browser: Use browser automation for JS-heavy sites

        Returns:
            Analysis result dictionary
        """
        payload = {
            "url": url,
            "options": {
                "screenshot": screenshot,
                "use_browser": use_browser
            }
        }

        response = self.session.post(f"{self.base_url}/api/v1/analyze", json=payload)
        response.raise_for_status()
        return response.json()

    def batch_analyze_websites(
        self,
        urls: List[str],
        webhook_url: Optional[str] = None,
        screenshot: bool = False
    ) -> Dict:
        """
        Analyze multiple websites in batch

        Args:
            urls: List of URLs to analyze
            webhook_url: Optional webhook URL for completion notification
            screenshot: Include screenshots

        Returns:
            Batch analysis response
        """
        payload = {
            "urls": urls,
            "options": {"screenshot": screenshot}
        }

        if webhook_url:
            payload["webhook_url"] = webhook_url

        response = self.session.post(f"{self.base_url}/api/v1/batch-analyze", json=payload)
        response.raise_for_status()
        return response.json()

    def get_batch_status(self, batch_id: str) -> Dict:
        """
        Get status of batch analysis

        Args:
            batch_id: Batch ID from batch_analyze_websites

        Returns:
            Batch status information
        """
        response = self.session.get(f"{self.base_url}/api/v1/batch-analyze/{batch_id}")
        response.raise_for_status()
        return response.json()

    def get_usage_stats(self) -> Dict:
        """
        Get API usage statistics

        Returns:
            Usage statistics
        """
        response = self.session.get(f"{self.base_url}/api/v1/usage")
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    client = PageIQClient("your-rapidapi-key-here")

    # Analyze single website
    try:
        result = client.analyze_website("https://example.com", screenshot=True)
        print("Analysis result:", result)
    except Exception as e:
        print("Error:", e)

    # Batch analysis
    try:
        batch_result = client.batch_analyze_websites([
            "https://example.com",
            "https://github.com"
        ], webhook_url="https://your-webhook-url.com/notify")
        print("Batch started:", batch_result)

        # Check status later
        import time
        time.sleep(30)  # Wait for processing
        status = client.get_batch_status(batch_result["data"]["batch_id"])
        print("Batch status:", status)
    except Exception as e:
        print("Error:", e)