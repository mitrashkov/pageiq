import asyncio
import logging
import platform
import os
from typing import Dict, Optional, Tuple
import inspect

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext
except Exception:  # pragma: no cover - optional dependency
    async_playwright = None  # type: ignore[assignment]
    Browser = BrowserContext = object  # type: ignore[misc,assignment]

from app.core.config import settings

logger = logging.getLogger(__name__)

def playwright_available() -> bool:
    return async_playwright is not None


class BrowserService:
    """Service for headless browser automation using Playwright."""

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
        # Force PLAYWRIGHT_BROWSERS_PATH for Render/Local
        # Using absolute path for Render Free Plan reliability
        render_root = '/opt/render/project/src'
        if os.path.exists(render_root):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(render_root, 'pw-browsers')
        else:
            # Local development fallback
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.abspath('./pw-browsers')
            
        logger.info(f"Forced PLAYWRIGHT_BROWSERS_PATH to {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def initialize(self):
        """Initialize Playwright browser."""
        try:
            if async_playwright is None:
                raise RuntimeError(
                    "Playwright is not installed. Install it with `pip install playwright` "
                    "and then run `playwright install`."
                )
            
            # Log current environment for debugging
            logger.info(f"Initializing browser. PLAYWRIGHT_BROWSERS_PATH={os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not Set')}")
            logger.info(f"HOME={os.environ.get('HOME', 'Not Set')}")

            started = async_playwright().start()
            # Tests patch `async_playwright` with a MagicMock; support both async and sync.
            self.playwright = await started if inspect.isawaitable(started) else started

            # Launch browser with anti-detection measures
            args = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ]

            # `--single-process` is not supported on Windows Chromium.
            if platform.system().lower() != "windows":
                args.append("--single-process")

            launched = self.playwright.chromium.launch(headless=True, args=args)
            self.browser = await launched if inspect.isawaitable(launched) else launched

            # Create context with realistic settings
            ctx = self.browser.new_context(
                user_agent=self._get_random_user_agent(),
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                geolocation=None,
                permissions=[],
            )
            self.context = await ctx if inspect.isawaitable(ctx) else ctx

            # Add anti-detection scripts
            await self.context.add_init_script("""
                // Override navigator properties
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

                // Override plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });

                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)

            logger.info("Browser service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser service cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def fetch_page(
        self,
        url: str,
        wait_for_network_idle: bool = True,
        timeout: int = 30000
    ) -> Tuple[Optional[str], Optional[str], Dict[str, str]]:
        """
        Fetch a page using browser automation.

        Args:
            url: URL to fetch
            wait_for_network_idle: Wait for network to be idle
            timeout: Timeout in milliseconds

        Returns:
            Tuple of (html_content, error_message, metadata)
        """
        if not self.context:
            await self.initialize()

        try:
            page = await self.context.new_page()

            # Set extra HTTP headers
            await page.set_extra_http_headers({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })

            # Navigate to page
            response = await page.goto(url, wait_until='domcontentloaded', timeout=timeout)

            if not response:
                await page.close()
                return None, f"No response from {url}", {}

            if not response.ok:
                await page.close()
                return None, f"HTTP {response.status}: {response.status_text}", {}

            # Wait for network idle if requested
            if wait_for_network_idle:
                await page.wait_for_load_state('networkidle', timeout=timeout)

            # Get final HTML content
            html_content = await page.content()

            # Get page metadata
            try:
                response_headers = dict(getattr(response, "headers", {}) or {})
            except Exception:
                response_headers = {}
            metadata = {
                'url': page.url,
                'title': await page.title(),
                'status_code': response.status,
                'content_type': response_headers.get('content-type', ''),
                'headers': response_headers,
            }

            await page.close()

            logger.info(f"Successfully fetched {len(html_content)} characters from {url} using browser")
            return html_content, None, metadata

        except Exception as e:
            error_msg = f"Browser fetch failed for {url}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, {}

    async def take_screenshot(
        self,
        url: str,
        full_page: bool = True,
        timeout: int = 30000
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Take a screenshot of a webpage.

        Args:
            url: URL to screenshot
            full_page: Whether to capture full page
            timeout: Timeout in milliseconds

        Returns:
            Tuple of (screenshot_bytes, error_message)
        """
        if not self.context:
            await self.initialize()

        try:
            page = await self.context.new_page()

            # Navigate to page
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            await page.wait_for_load_state('networkidle', timeout=timeout)

            # Take screenshot
            screenshot = await page.screenshot(full_page=full_page)

            await page.close()

            logger.info(f"Screenshot taken for {url}")
            return screenshot, None

        except Exception as e:
            error_msg = f"Screenshot failed for {url}: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    def _get_random_user_agent(self) -> str:
        """Get a random realistic user agent string."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
        ]

        import random
        return random.choice(user_agents)


# Global instance for sync usage (will be initialized on demand)
browser_service = BrowserService()