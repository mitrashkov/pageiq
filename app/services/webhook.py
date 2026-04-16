import httpx
import json
from typing import Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for sending webhook notifications"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    async def send_notification(
        self,
        webhook_url: str,
        event_type: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send webhook notification asynchronously

        Args:
            webhook_url: The webhook URL to send to
            event_type: Type of event (e.g., 'analysis.completed')
            payload: The data payload to send
            headers: Additional headers to include

        Returns:
            bool: True if successful, False otherwise
        """
        # Prepare webhook payload
        webhook_payload = {
            "event": event_type,
            "timestamp": payload.get("timestamp", "2026-04-16T18:58:41Z"),
            "data": payload
        }

        # Prepare headers
        webhook_headers = {
            "Content-Type": "application/json",
            "User-Agent": "PageIQ-Webhook/1.0",
            "X-Webhook-Event": event_type,
        }
        if headers:
            webhook_headers.update(headers)

        # Send webhook in background thread to avoid blocking
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            self.executor,
            self._send_http_request,
            webhook_url,
            webhook_payload,
            webhook_headers
        )

        return success

    def _send_http_request(
        self,
        url: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> bool:
        """
        Send HTTP request synchronously (called in thread pool)

        Args:
            url: Webhook URL
            payload: JSON payload
            headers: HTTP headers

        Returns:
            bool: True if successful
        """
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    url,
                    json=payload,
                    headers=headers
                )

                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Webhook sent successfully to {url}")
                    return True
                else:
                    logger.error(f"Webhook failed: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Webhook error for {url}: {str(e)}")
            return False

    async def send_analysis_complete_notification(
        self,
        webhook_url: str,
        request_id: str,
        analysis_result: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """
        Send notification for completed analysis

        Args:
            webhook_url: User's webhook URL
            request_id: Unique request identifier
            analysis_result: The analysis result data
            user_id: Optional user identifier

        Returns:
            bool: True if notification sent successfully
        """
        payload = {
            "request_id": request_id,
            "user_id": user_id,
            "status": "completed",
            "result": analysis_result,
            "timestamp": analysis_result.get("timestamp", "2026-04-16T18:58:41Z")
        }

        headers = {}
        if user_id:
            headers["X-User-ID"] = user_id

        return await self.send_notification(
            webhook_url,
            "analysis.completed",
            payload,
            headers
        )

    async def send_batch_complete_notification(
        self,
        webhook_url: str,
        batch_id: str,
        results: list,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Send notification for completed batch analysis

        Args:
            webhook_url: User's webhook URL
            batch_id: Unique batch identifier
            results: List of analysis results
            user_id: Optional user identifier

        Returns:
            bool: True if notification sent successfully
        """
        payload = {
            "batch_id": batch_id,
            "user_id": user_id,
            "status": "completed",
            "results_count": len(results),
            "results": results,
            "timestamp": "2026-04-16T18:58:41Z"
        }

        headers = {}
        if user_id:
            headers["X-User-ID"] = user_id

        return await self.send_notification(
            webhook_url,
            "batch_analysis.completed",
            payload,
            headers
        )


# Global webhook service instance
webhook_service = WebhookService()