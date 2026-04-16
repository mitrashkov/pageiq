from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.redis import get_redis


@dataclass
class BatchStatus:
    batch_id: str
    status: str  # queued|processing|completed|failed
    total_count: int
    completed_count: int
    failed_count: int
    created_at_ms: int
    updated_at_ms: int
    webhook_url: Optional[str] = None
    last_error: Optional[str] = None

    @property
    def progress(self) -> float:
        if self.total_count <= 0:
            return 0.0
        return min(1.0, max(0.0, self.completed_count / self.total_count))


class BatchStatusStore:
    def __init__(self):
        self.redis = get_redis()

    def _meta_key(self, batch_id: str) -> str:
        return f"batch:{batch_id}:meta"

    def _results_key(self, batch_id: str) -> str:
        return f"batch:{batch_id}:results"

    def init_batch(self, batch_id: str, total_count: int, webhook_url: Optional[str] = None) -> BatchStatus:
        now_ms = int(time.time() * 1000)
        status = BatchStatus(
            batch_id=batch_id,
            status="queued",
            total_count=total_count,
            completed_count=0,
            failed_count=0,
            created_at_ms=now_ms,
            updated_at_ms=now_ms,
            webhook_url=webhook_url,
        )
        self._save_status(status)
        # ensure results list exists
        self.redis.expire(self._results_key(batch_id), settings.BATCH_STATUS_TTL_SECONDS)
        return status

    def _save_status(self, status: BatchStatus) -> None:
        self.redis.set(
            self._meta_key(status.batch_id),
            json.dumps(asdict(status)),
            ex=settings.BATCH_STATUS_TTL_SECONDS,
        )

    def get_status(self, batch_id: str) -> Optional[BatchStatus]:
        raw = self.redis.get(self._meta_key(batch_id))
        if not raw:
            return None
        payload = json.loads(raw.decode("utf-8"))
        return BatchStatus(**payload)

    def set_processing(self, batch_id: str) -> None:
        status = self.get_status(batch_id)
        if not status:
            return
        status.status = "processing"
        status.updated_at_ms = int(time.time() * 1000)
        self._save_status(status)

    def record_result(self, batch_id: str, result: Dict[str, Any]) -> None:
        # Store in a list as JSON lines for incremental retrieval.
        self.redis.lpush(self._results_key(batch_id), json.dumps(result))
        self.redis.ltrim(self._results_key(batch_id), 0, 9999)
        self.redis.expire(self._results_key(batch_id), settings.BATCH_STATUS_TTL_SECONDS)

        status = self.get_status(batch_id)
        if not status:
            return
        status.completed_count += 1
        if not result.get("success", False):
            status.failed_count += 1
        status.updated_at_ms = int(time.time() * 1000)
        self._save_status(status)

    def set_completed(self, batch_id: str) -> None:
        status = self.get_status(batch_id)
        if not status:
            return
        status.status = "completed"
        status.updated_at_ms = int(time.time() * 1000)
        self._save_status(status)

    def set_failed(self, batch_id: str, error: str) -> None:
        status = self.get_status(batch_id)
        if not status:
            return
        status.status = "failed"
        status.last_error = error
        status.updated_at_ms = int(time.time() * 1000)
        self._save_status(status)

    def get_results(self, batch_id: str, limit: int = 1000) -> List[Dict[str, Any]]:
        raw_items = self.redis.lrange(self._results_key(batch_id), 0, max(0, int(limit) - 1))
        # lpush stores newest first; reverse to chronological order for API.
        raw_items = list(reversed(raw_items))
        results: List[Dict[str, Any]] = []
        for raw in raw_items:
            try:
                results.append(json.loads(raw.decode("utf-8")))
            except Exception:
                continue
        return results


batch_status_store = BatchStatusStore()

