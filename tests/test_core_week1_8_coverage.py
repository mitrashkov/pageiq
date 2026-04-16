import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.redis import _InMemoryRedis
from app.main import app
from app.services.analyzer import analyze_url
from app.services.batch_status import batch_status_store
from app.tasks.batch_tasks import _run_async, batch_analyze_task


@pytest.mark.asyncio
async def test_analyzer_robots_blocked():
    with patch("app.services.analyzer.robots_checker.can_fetch", return_value=False):
        with pytest.raises(PermissionError):
            await analyze_url("https://example.com", {})


@pytest.mark.asyncio
async def test_analyzer_use_browser_missing_playwright():
    with patch("app.services.analyzer.robots_checker.can_fetch", return_value=True), patch(
        "app.services.analyzer.playwright_available", return_value=False
    ):
        with pytest.raises(RuntimeError):
            await analyze_url("https://example.com", {"use_browser": True})


@pytest.mark.asyncio
async def test_analyzer_fetch_fallback_to_browser_and_screenshot_saved():
    html = "<html><head><title>T</title></head><body>Hello world</body></html>"

    async_browser = AsyncMock()
    async_browser.fetch_page.return_value = (html, None, {"headers": {"server": "nginx"}})
    # async context manager
    async_cm = AsyncMock()
    async_cm.__aenter__.return_value = async_browser
    async_cm.__aexit__.return_value = None

    with patch("app.services.analyzer.robots_checker.can_fetch", return_value=True), patch(
        "app.services.analyzer.html_fetcher.fetch_html", return_value=(None, "fail", {})
    ), patch("app.services.analyzer.playwright_available", return_value=True), patch(
        "app.services.analyzer.browser_service", async_cm
    ), patch(
        "app.services.analyzer.screenshot_service.capture_screenshot", new_callable=AsyncMock
    ) as cap, patch(
        "app.services.analyzer.screenshot_service.save_screenshot", return_value="/screenshots/x.png"
    ) as save:
        cap.return_value = (b"png", None)
        data, _ = await analyze_url(
            "https://example.com",
            {"screenshot": True, "screenshot_filename": "x.png"},
        )
        assert data["url"] == "https://example.com"
        assert data["screenshot_url"] == "/screenshots/x.png"
        save.assert_called()


@pytest.mark.asyncio
async def test_analyzer_use_browser_success_and_missing_html_raises():
    html = "<html><head><title>Shop</title></head><body>checkout cart</body></html>"

    async_browser = AsyncMock()
    async_browser.fetch_page.return_value = (html, None, {"headers": {}})
    async_cm = AsyncMock()
    async_cm.__aenter__.return_value = async_browser
    async_cm.__aexit__.return_value = None

    with patch("app.services.analyzer.robots_checker.can_fetch", return_value=True), patch(
        "app.services.analyzer.playwright_available", return_value=True
    ), patch("app.services.analyzer.browser_service", async_cm):
        data, _ = await analyze_url("https://example.com", {"use_browser": True})
        assert data["industry_guess"] is not None

    with patch("app.services.analyzer.robots_checker.can_fetch", return_value=True), patch(
        "app.services.analyzer.html_fetcher.fetch_html", return_value=(None, None, {})
    ):
        with pytest.raises(RuntimeError):
            await analyze_url("https://example.com", {})


def test_analyze_endpoint_screenshot_and_500_handler():
    client = TestClient(app)

    with patch("app.api.v1.endpoints.analyze.analyze_url_core", new_callable=AsyncMock) as core:
        core.return_value = ({"url": "https://example.com"}, 1)
        resp = client.post("/api/v1/analyze", json={"url": "https://example.com", "options": {"screenshot": True}})
        assert resp.status_code == 200

    with patch("app.api.v1.endpoints.analyze.analyze_url_core", new_callable=AsyncMock) as core:
        core.side_effect = Exception("boom")
        resp = client.post("/api/v1/analyze", json={"url": "https://example.com", "options": {}})
        assert resp.status_code == 500


def test_batch_endpoint_validation_paths():
    client = TestClient(app)
    resp = client.post("/api/v1/batch-analyze/", json={"urls": ["https://e.com"] * 101, "options": {}})
    assert resp.status_code == 400
    resp2 = client.post("/api/v1/batch-analyze/", json={"urls": [], "options": {}})
    assert resp2.status_code == 400


def test_batch_status_store_failure_path_and_results():
    batch_id = "b1"
    batch_status_store.init_batch(batch_id, total_count=2)
    batch_status_store.set_processing(batch_id)
    batch_status_store.record_result(batch_id, {"url": "a", "success": False, "error": "x"})
    batch_status_store.record_result(batch_id, {"url": "b", "success": True, "data": {}})
    batch_status_store.set_completed(batch_id)
    batch_status_store.set_failed(batch_id, "boom")

    status = batch_status_store.get_status(batch_id)
    assert status is not None
    assert status.failed_count >= 1
    assert status.last_error == "boom"
    results = batch_status_store.get_results(batch_id)
    assert len(results) == 2


def test_inmemory_redis_string_list_zset_and_scan_iter():
    r = _InMemoryRedis()
    assert r.ping() is True

    # strings
    assert r.get("k") is None
    r.set("k", "1")
    assert r.get("k") == b"1"
    assert r.incr("k", 2) == 3

    # lists
    r.lpush("l", "a")
    r.lpush("l", "b")
    assert r.lrange("l", 0, -1) == [b"b", b"a"]
    r.ltrim("l", 0, 0)
    assert r.lrange("l", 0, -1) == [b"b"]

    # sorted sets top items
    r.zincrby("z", 1, "x")
    r.zincrby("z", 2, "y")
    items = r.zrange("z", 0, -1, withscores=True)
    assert (b"x", 1.0) in items
    assert (b"y", 2.0) in items
    removed = r.zremrangebyrank("z", 0, 0)
    assert removed == 1

    # scan
    keys = set(k.decode("utf-8") for k in r.scan_iter("k*"))
    assert "k" in keys
    r.set("ttl", "x", ex=1)
    r._expires_at["ttl"] = 0  # force expiry
    assert r.get("ttl") is None


def test_get_redis_falls_back_to_inmemory(monkeypatch):
    from app.core import redis as redis_module

    monkeypatch.setattr(redis_module.redis, "from_url", lambda *_args, **_kwargs: (_ for _ in ()).throw(Exception("no")))
    redis_module._redis_singleton = None
    client = redis_module.get_redis()
    assert isinstance(client, redis_module._InMemoryRedis)


@pytest.mark.asyncio
async def test_run_async_inside_running_loop():
    async def coro():
        await asyncio.sleep(0)
        return 123

    assert _run_async(coro()) == 123


def test_run_async_outside_loop_and_batch_task_error_and_webhook_branch():
    async def coro():
        return 7

    assert _run_async(coro()) == 7

    async def failing(url: str, options: dict):
        raise RuntimeError("nope")

    async def ok(url: str, options: dict):
        return ({"url": url}, 0)

    with patch("app.tasks.batch_tasks.analyze_url", new=failing):
        res = batch_analyze_task(batch_id="bx", urls=["https://e.com"], options={}, webhook_url=None)
        assert res["results_count"] == 1

    with patch("app.tasks.batch_tasks.analyze_url", new=ok), patch(
        "app.tasks.batch_tasks.webhook_service.send_batch_complete_notification", new_callable=AsyncMock
    ) as wh:
        res = batch_analyze_task(
            batch_id="by", urls=["https://e.com"], options={"screenshot": True}, webhook_url="https://hook"
        )
        assert res["results_count"] == 1
        wh.assert_called()

    # Outer exception path
    with patch("app.tasks.batch_tasks.analyze_url", new=ok), patch(
        "app.tasks.batch_tasks.batch_status_store.set_completed", side_effect=RuntimeError("x")
    ):
        with pytest.raises(RuntimeError):
            batch_analyze_task(batch_id="bz", urls=["https://e.com"], options={}, webhook_url=None)

