import pytest
from unittest.mock import AsyncMock, patch

from app.services.browser import BrowserService
from app.services.screenshot import ScreenshotService


class TestBrowserService:
    @pytest.mark.asyncio
    async def test_browser_initialization(self):
        """Test browser service initialization."""
        service = BrowserService()

        # Mock playwright
        with patch('app.services.browser.async_playwright') as mock_playwright:
            mock_browser = AsyncMock()
            mock_context = AsyncMock()

            mock_playwright.return_value.start.return_value.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context

            await service.initialize()

            assert service.browser == mock_browser
            assert service.context == mock_context

            await service.cleanup()

    @pytest.mark.asyncio
    async def test_fetch_page_success(self):
        """Test successful page fetching."""
        service = BrowserService()

        with patch('app.services.browser.async_playwright') as mock_playwright:
            mock_page = AsyncMock()
            mock_response = AsyncMock()
            mock_response.ok = True
            mock_response.status = 200

            mock_page.goto.return_value = mock_response
            mock_page.wait_for_load_state.return_value = None
            mock_page.content.return_value = '<html><body>Test</body></html>'
            mock_page.title.return_value = 'Test Page'
            mock_page.url = 'https://example.com'

            mock_context = AsyncMock()
            mock_context.new_page.return_value = mock_page

            mock_browser = AsyncMock()
            mock_browser.new_context.return_value = mock_context

            mock_playwright.return_value.start.return_value.chromium.launch.return_value = mock_browser

            await service.initialize()

            html, error, metadata = await service.fetch_page('https://example.com')

            assert html == '<html><body>Test</body></html>'
            assert error is None
            assert metadata['title'] == 'Test Page'

            await service.cleanup()

    @pytest.mark.asyncio
    async def test_take_screenshot(self):
        """Test screenshot capture."""
        service = BrowserService()

        with patch('app.services.browser.async_playwright') as mock_playwright:
            mock_page = AsyncMock()
            mock_page.screenshot.return_value = b'fake_screenshot_data'

            mock_context = AsyncMock()
            mock_context.new_page.return_value = mock_page

            mock_browser = AsyncMock()
            mock_browser.new_context.return_value = mock_context

            mock_playwright.return_value.start.return_value.chromium.launch.return_value = mock_browser

            await service.initialize()

            screenshot, error = await service.take_screenshot('https://example.com')

            assert screenshot == b'fake_screenshot_data'
            assert error is None

            await service.cleanup()


class TestScreenshotService:
    @pytest.mark.asyncio
    async def test_capture_screenshot(self):
        """Test screenshot service."""
        service = ScreenshotService()

        with patch.object(service.browser_service, 'take_screenshot', new_callable=AsyncMock) as mock_screenshot:
            mock_screenshot.return_value = (b'fake_data', None)

            screenshot, error = await service.capture_screenshot('https://example.com')

            assert screenshot == b'fake_data'
            assert error is None

    def test_save_screenshot(self):
        """Test screenshot saving."""
        service = ScreenshotService()

        filename = 'test.png'
        url = service.save_screenshot(b'fake_data', filename)

        assert url.startswith("/screenshots/")
        assert url.endswith(filename)