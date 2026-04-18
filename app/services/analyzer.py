from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

from bs4 import BeautifulSoup

import app.services as services
from app.services.browser import browser_service, playwright_available
from app.services import extractors as extractors_service
from app.services.fetcher import html_fetcher
from app.services.robots_checker import robots_checker
from app.services.screenshot import screenshot_service
from app.services.industry_detector import guess_industry


async def analyze_url(
    url: str,
    options: Dict[str, Any],
) -> Tuple[Dict[str, Any], int]:
    """
    Core analysis pipeline shared by API endpoint and batch tasks.

    Returns (data, processing_time_ms).
    """
    start_time = time.time()

    # Respect robots.txt by default
    if not robots_checker.can_fetch(url):
        raise PermissionError("Crawling not allowed by robots.txt")

    use_browser = bool(options.get("use_browser", False))
    
    # Plan check for JS Rendering (Playwright) - Temporarily enabled for BASIC
    # BASIC gets NO browser by default. PRO gets limited. ULTRA/MEGA get FULL access.
    user_plan = options.get("user_plan", "free").lower()
    if use_browser and user_plan in ["free"]:
        raise PermissionError(f"JavaScript Rendering is a PRO/ULTRA/MEGA feature. Your current plan is: {user_plan.upper()}")

    if use_browser and not playwright_available():
        raise RuntimeError("Browser analysis requested but Playwright is not installed")

    html_content: Optional[str] = None
    headers: Dict[str, str] = {}
    browser_metadata: Dict[str, Any] = {}
    diagnostics = {
        "fetch_method": None,
        "http_error": None,
        "browser_error": None,
        "fallback_to_browser": False,
        "final_status": None,
    }

    if use_browser:
        diagnostics["fetch_method"] = "browser"
        async with browser_service as browser:
            html_content, error, browser_metadata = await browser.fetch_page(
                url,
                wait_for_network_idle=bool(options.get("wait_for_network_idle", True)),
            )
            if error:
                diagnostics["browser_error"] = error
                diagnostics["final_status"] = "browser_failed"
                raise RuntimeError(error)
            headers = browser_metadata.get("headers", {}) if isinstance(browser_metadata, dict) else {}
            diagnostics["final_status"] = "browser_success"
    else:
        diagnostics["fetch_method"] = "http"
        html_content, error, headers = html_fetcher.fetch_html(url)
        if error:
            diagnostics["http_error"] = error
            diagnostics["fallback_to_browser"] = True
            if not playwright_available():
                diagnostics["final_status"] = "http_failed_no_browser"
                raise RuntimeError(error)
            async with browser_service as browser:
                html_content, error, browser_metadata = await browser.fetch_page(url)
                if error:
                    diagnostics["browser_error"] = error
                    diagnostics["final_status"] = "browser_failed"
                    raise RuntimeError(error)
                headers = browser_metadata.get("headers", {}) if isinstance(browser_metadata, dict) else {}
                diagnostics["final_status"] = "browser_success"
        else:
            diagnostics["final_status"] = "http_success"


    if not html_content:
        diagnostics["final_status"] = "no_content"
        raise RuntimeError("Unable to fetch webpage content")


    soup = html_fetcher.parse_html(html_content)
    if not soup:
        diagnostics["final_status"] = "parse_failed"
        raise RuntimeError("Unable to parse HTML content")
    if not isinstance(soup, BeautifulSoup):
        soup = BeautifulSoup(html_content, "html.parser")

    title = extractors_service.extract_title(soup)
    description = extractors_service.extract_description(soup)
    favicon = extractors_service.extract_favicon(soup, url)
    logo = extractors_service.extract_logo(soup, url)
    emails = extractors_service.extract_emails(soup)
    phones = extractors_service.extract_phones(soup)
    social_profiles = extractors_service.extract_social_profiles(soup, url)
    language = extractors_service.detect_language(soup)
    country = extractors_service.detect_country(url, soup)
    keywords = extractors_service.extract_keywords(soup)
    schema_org = extractors_service.extract_schema_org(soup)
    open_graph = extractors_service.extract_open_graph(soup)

    tech_stack = services.tech_detector.detect_technologies(soup, html_content, headers)

    processing_time_ms = int((time.time() - start_time) * 1000)

    content_size = len(html_content)
    speed_score = services.speed_scorer.calculate_score(processing_time_ms, content_size)

    ai_summary = None
    if title or description:
        summary_text = f"{title or ''} {description or ''}".strip()
        if summary_text:
            ai_summary = services.ai_summarizer.generate_summary(summary_text)

    screenshot_url = None
    if options.get("screenshot", False):
        screenshot_data, screenshot_error = await screenshot_service.capture_screenshot(
            url,
            full_page=bool(options.get("full_page_screenshot", True)),
        )
        if screenshot_data and not screenshot_error:
            # Caller provides filename/id.
            filename = options.get("screenshot_filename")
            if filename:
                screenshot_url = screenshot_service.save_screenshot(screenshot_data, str(filename))


    data = {
        "url": url,
        "title": title,
        "description": description,
        "logo": logo,
        "favicon": favicon,
        "emails": emails,
        "phones": phones,
        "socials": social_profiles,
        "tech_stack": tech_stack,
        "industry_guess": None,
        "language": language,
        "country_guess": country,
        "keywords": keywords,
        "schema_org": schema_org,
        "og_tags": open_graph,
        "screenshot_url": screenshot_url,
        "page_speed_score": speed_score,
        "ai_summary": ai_summary,
        "timestamp": int(time.time() * 1000),
        "processing_time_ms": processing_time_ms,
        "diagnostics": diagnostics,
    }

    industry = guess_industry(
        title=title,
        description=description,
        keywords=keywords,
        tech_stack=tech_stack,
    )
    if industry:
        data["industry_guess"] = {"label": industry.label, "confidence": industry.confidence}

    return data, processing_time_ms

