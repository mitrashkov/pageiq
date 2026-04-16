from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from app.core.celery_app import celery_app
from app.services.analyzer import analyze_url
from app.services.batch_status import batch_status_store
from app.services.webhook import webhook_service


_executor = ThreadPoolExecutor(max_workers=4)


def _run_async(coro):
    """
    Run an async coroutine from sync code.

    If we're already inside a running event loop (e.g. Celery eager execution
    triggered within an async request handler), run the coroutine in a fresh
    thread with its own loop.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    future = _executor.submit(asyncio.run, coro)
    return future.result()


@celery_app.task(name="pageiq.batch_analyze")
def batch_analyze_task(batch_id: str, urls: List[str], options: Dict[str, Any], webhook_url: Optional[str] = None):
    """
    Celery task that runs batch analysis and writes incremental status/results to Redis.
    """
    batch_status_store.set_processing(batch_id)

    results: List[Dict[str, Any]] = []
    try:
        for url in urls:
            try:
                # Ensure each screenshot gets a stable filename.
                per_options = dict(options or {})
                if per_options.get("screenshot"):
                    per_options["screenshot_filename"] = f"{batch_id}-{abs(hash(url))}.png"

                data, _ = _run_async(analyze_url(url, per_options))
                result = {"url": url, "success": True, "data": data}
            except Exception as e:
                result = {"url": url, "success": False, "error": str(e)}

            batch_status_store.record_result(batch_id, result)
            results.append(result)

        batch_status_store.set_completed(batch_id)

        if webhook_url:
            _run_async(
                webhook_service.send_batch_complete_notification(
                    webhook_url=webhook_url,
                    batch_id=batch_id,
                    results=results,
                    user_id=None,
                )
            )

        return {"batch_id": batch_id, "status": "completed", "results_count": len(results)}
    except Exception as e:
        batch_status_store.set_failed(batch_id, str(e))
        raise

