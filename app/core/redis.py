from __future__ import annotations

import time
from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, Iterable, List, Optional, Tuple

import redis
from redis import Redis

from app.core.config import settings


@dataclass
class _InMemoryRedis:
    """
    Minimal in-memory Redis substitute for tests/dev when Redis isn't running.

    Supports the subset of commands used by `RateLimiter`:
    - ZSET ops: zadd, zcard, zrange(withscores), zremrangebyscore
    - expire (no-op TTL cleanup is handled opportunistically)
    - ping

    Also supports a small subset used by analytics/batch status:
    - Strings: get, set, incr
    - Lists: lpush, lrange, ltrim
    - Sorted sets: zincrby, zremrangebyrank
    - Key scanning: scan_iter
    """

    _zsets: Dict[str, List[Tuple[float, str]]] = field(default_factory=dict)
    _expires_at: Dict[str, float] = field(default_factory=dict)
    _strings: Dict[str, str] = field(default_factory=dict)
    _lists: Dict[str, List[str]] = field(default_factory=dict)

    def _cleanup(self, key: str):
        exp = self._expires_at.get(key)
        if exp is not None and exp <= time.time():
            self._zsets.pop(key, None)
            self._strings.pop(key, None)
            self._lists.pop(key, None)
            self._expires_at.pop(key, None)

    def ping(self) -> bool:
        return True

    def zremrangebyscore(self, key: str, min_score: float, max_score: float) -> int:
        self._cleanup(key)
        items = self._zsets.get(key, [])
        before = len(items)
        self._zsets[key] = [(s, m) for (s, m) in items if not (min_score <= s <= max_score)]
        return before - len(self._zsets[key])

    def zcard(self, key: str) -> int:
        self._cleanup(key)
        return len(self._zsets.get(key, []))

    def zrange(self, key: str, start: int, end: int, withscores: bool = False):
        self._cleanup(key)
        items = sorted(self._zsets.get(key, []), key=lambda t: t[0])
        if end == -1:
            sliced = items[start:]
        else:
            sliced = items[start : end + 1]
        if withscores:
            return [(m.encode("utf-8"), s) for (s, m) in sliced]
        return [m.encode("utf-8") for (s, m) in sliced]

    def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        self._cleanup(key)
        items = self._zsets.setdefault(key, [])
        added = 0
        for member, score in mapping.items():
            items.append((float(score), str(member)))
            added += 1
        return added

    def expire(self, key: str, seconds: int) -> bool:
        self._expires_at[key] = time.time() + int(seconds)
        return True

    # ---- Strings ----
    def get(self, key: str):
        self._cleanup(key)
        val = self._strings.get(key)
        if val is None:
            return None
        return val.encode("utf-8")

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._cleanup(key)
        self._strings[key] = str(value)
        if ex is not None:
            self.expire(key, ex)
        return True

    def incr(self, key: str, amount: int = 1) -> int:
        self._cleanup(key)
        cur = int(self._strings.get(key, "0") or "0")
        cur += int(amount)
        self._strings[key] = str(cur)
        return cur

    # ---- Lists ----
    def lpush(self, key: str, value: str) -> int:
        self._cleanup(key)
        lst = self._lists.setdefault(key, [])
        lst.insert(0, str(value))
        return len(lst)

    def ltrim(self, key: str, start: int, end: int) -> bool:
        self._cleanup(key)
        lst = self._lists.get(key, [])
        if end == -1:
            self._lists[key] = lst[start:]
        else:
            self._lists[key] = lst[start : end + 1]
        return True

    def lrange(self, key: str, start: int, end: int) -> List[bytes]:
        self._cleanup(key)
        lst = self._lists.get(key, [])
        if end == -1:
            sliced = lst[start:]
        else:
            sliced = lst[start : end + 1]
        return [v.encode("utf-8") for v in sliced]

    # ---- Sorted sets (analytics “top items”) ----
    def zincrby(self, key: str, amount: float, value: str) -> float:
        self._cleanup(key)
        items = self._zsets.setdefault(key, [])
        # store member->score in list; update if exists
        for i, (score, member) in enumerate(items):
            if member == value:
                new_score = score + float(amount)
                items[i] = (new_score, member)
                return new_score
        items.append((float(amount), str(value)))
        return float(amount)

    def zremrangebyrank(self, key: str, start: int, end: int) -> int:
        self._cleanup(key)
        items = sorted(self._zsets.get(key, []), key=lambda t: t[0])
        if not items:
            return 0
        # Redis ranks are ascending; support negative indexing like redis-py
        n = len(items)
        if start < 0:
            start = n + start
        if end < 0:
            end = n + end
        start = max(0, start)
        end = min(n - 1, end)
        if start > end:
            return 0
        removed = items[start : end + 1]
        remain = items[:start] + items[end + 1 :]
        self._zsets[key] = remain
        return len(removed)

    # ---- Key scanning ----
    def scan_iter(self, match: str) -> Iterable[bytes]:
        keys = set(self._strings.keys()) | set(self._lists.keys()) | set(self._zsets.keys())
        for key in keys:
            self._cleanup(key)
            if fnmatch(key, match.replace(":", ":")) and fnmatch(key, match):
                yield key.encode("utf-8")


_redis_singleton: Optional[Redis] = None


def get_redis() -> Redis:
    """Get Redis client instance (falls back to in-memory if unavailable)."""
    global _redis_singleton
    if _redis_singleton is not None:
        return _redis_singleton

    try:
        client: Redis = redis.from_url(settings.REDIS_URL)
        client.ping()
        _redis_singleton = client
        return client
    except Exception:
        # No Redis in local/test environment.
        _redis_singleton = _InMemoryRedis()  # type: ignore[assignment]
        return _redis_singleton


def test_redis_connection() -> bool:
    """Test Redis connection (True if real Redis reachable)."""
    try:
        client = redis.from_url(settings.REDIS_URL)
        client.ping()
        return True
    except Exception:
        return False