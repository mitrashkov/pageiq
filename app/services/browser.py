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

    _instance = None
    _lock = asyncio.Lock()
    # Global limit of concurrent browser pages. 
    # Render Free Plan (512MB) is extremely tight, so we use 2.
    _semaphore = asyncio.Semaphore(2) 

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._initialized = False
        
        # Force PLAYWRIGHT_BROWSERS_PATH for Render/Local
        # Using .playwright in the project root as it's the most common convention
        render_root = '/opt/render/project/src'
        if os.path.exists(render_root):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.join(render_root, '.playwright')
        else:
            # Local development fallback
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.abspath('./.playwright')
            
        logger.info(f"Forced PLAYWRIGHT_BROWSERS_PATH to {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
        if os.path.exists(os.environ['PLAYWRIGHT_BROWSERS_PATH']):
            logger.info(f"Browser path exists. Contents: {os.listdir(os.environ['PLAYWRIGHT_BROWSERS_PATH'])}")
        else:
            logger.warning(f"Browser path DOES NOT EXIST: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")

    async def __aenter__(self):
        # We don't initialize here anymore as it's a long-lived service
        # Instead, we just ensure it is initialized when needed
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # We DO NOT cleanup here anymore, we want the browser to stay alive
        # for subsequent requests to save memory and CPU.
        pass

    async def initialize(self):
        """Initialize Playwright browser."""
        if self._initialized:
            return
            
        try:
            if async_playwright is None:
                raise RuntimeError(
                    "Playwright is not installed. Install it with `pip install playwright` "
                    "and then run `playwright install`."
                )
            
            # Log current environment for debugging
            logger.info(f"Initializing long-lived browser service. PLAYWRIGHT_BROWSERS_PATH={os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not Set')}")
            logger.info(f"HOME={os.environ.get('HOME', 'Not Set')}")

            started = async_playwright().start()
            # Tests patch `async_playwright` with a MagicMock; support both async and sync.
            self.playwright = await started if inspect.isawaitable(started) else started

            # Launch browser with extreme memory-saving measures for Render Free Plan
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
                '--js-flags="--max-old-space-size=128"', # Limit V8 memory
                '--disable-extensions',
                '--disable-component-update',
                '--disable-default-apps',
                '--mute-audio',
            ]

            # `--single-process` is not supported on Windows Chromium.
            if platform.system().lower() != "windows":
                args.append("--single-process")

            launched = self.playwright.chromium.launch(headless=True, args=args)
            self.browser = await launched if inspect.isawaitable(launched) else launched

            # Create context with realistic settings
            # We use a single context and rotate pages within it
            ctx = self.browser.new_context(
                user_agent=self._get_random_user_agent(),
                viewport={'width': 1280, 'height': 800}, # Smaller viewport to save memory
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

            self._initialized = True
            logger.info("Browser service initialized successfully (long-lived)")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            raise

    async def cleanup(self):
        """Clean up browser resources (should be called on app shutdown)."""
        try:
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            self._initialized = False
            logger.info("Browser service cleaned up completely")
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
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self.initialize()

        async with self._semaphore:
            page = None
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
                # Use 'domcontentloaded' for speed, then 'networkidle' if requested
                response = await page.goto(url, wait_until='domcontentloaded', timeout=timeout)

                if not response:
                    return None, f"No response from {url}", {}

                if not response.ok:
                    return None, f"HTTP {response.status}: {response.status_text}", {}

                # Wait for network idle if requested
                if wait_for_network_idle:
                    try:
                        await page.wait_for_load_state('networkidle', timeout=min(timeout, 10000)) # Cap network idle wait
                    except Exception:
                        logger.warning(f"Timeout waiting for networkidle on {url}, continuing with current content")

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

                logger.info(f"Successfully fetched {len(html_content)} characters from {url} using browser")
                return html_content, None, metadata

            except Exception as e:
                error_msg = f"Browser fetch failed for {url}: {str(e)}"
                logger.error(error_msg)
                return None, error_msg, {}
            finally:
                if page:
                    await page.close()

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
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await self.initialize()

        async with self._semaphore:
            page = None
            try:
                page = await self.context.new_page()

                # Navigate to page
                await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                try:
                    await page.wait_for_load_state('networkidle', timeout=min(timeout, 10000))
                except Exception:
                    pass

                # Take screenshot
                screenshot = await page.screenshot(full_page=full_page)

                logger.info(f"Screenshot taken for {url}")
                return screenshot, None

            except Exception as e:
                error_msg = f"Screenshot failed for {url}: {str(e)}"
                logger.error(error_msg)
                return None, error_msg
            finally:
                if page:
                    await page.close()

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