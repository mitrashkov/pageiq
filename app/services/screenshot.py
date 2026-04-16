import logging
import os
from pathlib import Path
from typing import Optional, Tuple

from app.services.browser import browser_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class ScreenshotService:
    """Service for capturing website screenshots."""

    def __init__(self):
        self.browser_service = browser_service

    async def capture_screenshot(
        self,
        url: str,
        full_page: bool = True,
        timeout: int = 30000
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Capture a screenshot of a webpage.

        Args:
            url: URL to screenshot
            full_page: Whether to capture full page or viewport only
            timeout: Timeout in milliseconds

        Returns:
            Tuple of (screenshot_bytes, error_message)
        """
        # Let the browser service lazily initialize as needed.
        return await self.browser_service.take_screenshot(url, full_page, timeout)

    def save_screenshot(self, screenshot_data: bytes, filename: str) -> str:
        """
        Save screenshot data to file.

        Args:
            screenshot_data: Screenshot bytes
            filename: Filename to save as

        Returns:
            File path where screenshot was saved
        """
        screenshots_dir = Path(settings.SCREENSHOTS_DIR)
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        safe_name = os.path.basename(filename)
        target = screenshots_dir / safe_name
        target.write_bytes(screenshot_data)

        prefix = settings.SCREENSHOTS_URL_PREFIX.rstrip("/")
        return f"{prefix}/{safe_name}"


# Global instance
screenshot_service = ScreenshotService()