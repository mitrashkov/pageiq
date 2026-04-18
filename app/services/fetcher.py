import logging
import random
import time
from typing import Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.config import settings

logger = logging.getLogger(__name__)


class HTMLFetcher:
    """Service for fetching HTML content from URLs with retry logic and anti-bot evasion."""

    def __init__(self):
        self.session = self._create_session()
        self.user_agents = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        ]
        self.current_ua_index = 0

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default timeout
        session.timeout = 30

        return session

    async def fetch_html_async(self, url: str, timeout: int = 30, use_browser: bool = False, wait_for_network_idle: bool = True) -> Tuple[Optional[str], Optional[str], Dict[str, str]]:
        """
        Asynchronous version of fetch_html that supports browser rendering and automatic fallback.
        """
        if use_browser:
            from app.services.browser import browser_service
            async with browser_service as browser:
                return await browser.fetch_page(url, timeout=timeout * 1000, wait_for_network_idle=wait_for_network_idle)
        
        # Try standard fetch first
        html, error, headers = await asyncio.to_thread(self.fetch_html, url, timeout)
        
        # If standard fetch fails with a 403 (Forbidden) or 401 (Unauthorized), 
        # or other client errors, automatically retry with browser if possible.
        if error and ("403" in error or "401" in error or "400" in error):
            logger.info(f"Standard fetch failed for {url} ({error}). Retrying with browser...")
            from app.services.browser import browser_service
            async with browser_service as browser:
                return await browser.fetch_page(url, timeout=timeout * 1000, wait_for_network_idle=wait_for_network_idle)
                
        return html, error, headers

    def fetch_html(self, url: str, timeout: int = 30) -> Tuple[Optional[str], Optional[str], Dict[str, str]]:
        """
        Fetch HTML content from a URL with anti-bot evasion.

        Args:
            url: The URL to fetch
            timeout: Request timeout in seconds
            use_browser: Whether to use browser automation for JavaScript sites

        Returns:
            Tuple of (html_content, error_message, headers)
        """
        # Rotate user agents
        user_agent = self._get_next_user_agent()

        try:
            headers = self._build_headers(user_agent)

            # Add random delay to avoid detection (0.5-2 seconds)
            import time
            import random
            time.sleep(random.uniform(0.5, 2.0))

            logger.info(f"Fetching URL: {url} with UA: {user_agent[:50]}...")
            response = self.session.get(
                url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True
            )

            response.raise_for_status()

            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return None, f"Content type {content_type} is not HTML", dict(response.headers)

            # Decode content
            html_content = response.text

            # Add more realistic behavior - sometimes follow links
            self._simulate_human_behavior()

            logger.info(f"Successfully fetched {len(html_content)} characters from {url}")
            return html_content, None, dict(response.headers)

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch {url}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, {}
        except Exception as e:
            error_msg = f"Unexpected error fetching {url}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, {}

    def _get_next_user_agent(self) -> str:
        """Get next user agent in rotation."""
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return ua

    def _build_headers(self, user_agent: str) -> Dict[str, str]:
        """Build realistic HTTP headers."""
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    def _simulate_human_behavior(self):
        """Simulate human-like browsing behavior."""
        # Occasionally add extra processing time
        if random.random() < 0.3:  # 30% chance
            time.sleep(random.uniform(1.0, 3.0))

    def parse_html(self, html_content: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content with BeautifulSoup.
        Uses lxml for speed and robustness, with fallback to html.parser.

        Args:
            html_content: Raw HTML string

        Returns:
            BeautifulSoup object or None if parsing fails
        """
        if not html_content or not isinstance(html_content, str):
            return None

        try:
            # Try parsing with lxml first (fastest and most robust)
            soup = BeautifulSoup(html_content, 'lxml')
            
            # If lxml results in an empty soup (no tags), try html.parser as fallback
            if not soup.find():
                soup = BeautifulSoup(html_content, 'html.parser')
                
            # Final check: do we have ANY tags?
            if not soup.find():
                # If still no tags, it might just be a plain text page.
                # We'll return the soup anyway so extractors can still look at text_content
                return soup
                
            return soup
        except Exception as e:
            logger.error(f"Failed to parse HTML with lxml/html.parser: {str(e)}")
            try:
                # Last resort fallback
                return BeautifulSoup(html_content, 'html.parser')
            except Exception:
                return None


# Global instance
html_fetcher = HTMLFetcher()