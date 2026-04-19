# PageIQ API Documentation (Comprehensive Reference)

This document is the full, implementation-aligned guide for the current PageIQ codebase. It covers API surface area, request and response contracts, plan-gating behavior, operational notes, route aliases, and practical integration guidance.

If you are integrating PageIQ in production, read this file alongside:
- `app/api/v1/api.py` (router map)
- `app/api/v1/endpoints/*.py` (endpoint logic)
- `app/core/responses.py` (envelope contracts)

## 1. Platform Summary

PageIQ turns a URL into structured business intelligence. Core capabilities include:
- Full website analysis (`/api/v1/analyze`)
- Technology and language detection (`/api/v1/analyze/tech`)
- Contact extraction (`/api/v1/extract/emails`)
- Metadata and structured-data extraction (`/api/v1/extract/schema`, `/api/v1/extract/metadata`)
- SEO diagnostics (`/api/v1/seo/seo-audit`)
- Link quality checks (`/api/v1/seo/broken-links`)
- Usage analytics (`/api/v1/analytics/*`)
- Subscription and billing management (`/api/v1/account/*`)

In addition to API routes, PageIQ serves a retro-style marketing and SEO website with intent-focused landing pages.

## 2. Base URLs

- Production root: `https://pageiq.pompora.dev`
- API v1 base: `https://pageiq.pompora.dev/api/v1`
- Root docs page: `https://pageiq.pompora.dev/docs`

## 3. Authentication and Access

Authentication is managed through middleware and endpoint dependencies.

Common header format:

```http
X-API-Key: YOUR_API_KEY
```

Notes:
- `get_optional_user` is used on many analysis and extraction routes.
- `get_current_user` is used on account and billing routes, which require authenticated user context.
- Some plan-specific features are enforced in endpoint logic (details below).

## 4. Response Contracts

PageIQ uses two response styles:

## 4.1 Envelope Responses (`APIResponse.success` / `APIResponse.error`)

Defined in `app/core/responses.py`.

Success envelope:

```json
{
  "success": true,
  "data": {},
  "message": "Optional message",
  "request_id": "Optional request id",
  "processing_time_ms": 1234,
  "quota_remaining": 99
}
```

Error envelope:

```json
{
  "success": false,
  "error": {
    "message": "Error message",
    "code": "OPTIONAL_ERROR_CODE",
    "details": {}
  },
  "request_id": "Optional request id"
}
```

Headers often added:
- `X-API-Version`
- `X-Request-ID` (when present)
- `X-Processing-Time-MS` (when provided)

## 4.2 Direct Model Responses

Several endpoints return direct model-serialized JSON (not wrapped in `success/data`). This pattern is used by:
- `extract/*`
- `seo/*`
- `health/*`
- `analyze/tech`

When implementing clients, always branch parsing by endpoint family.

## 5. Routing Map (Current)

Top-level router mounts:
- `/api/v1/health`
- `/api/v1/analyze`
- `/api/v1/analytics`
- `/api/v1/extract`
- `/api/v1/seo`
- `/api/v1/account`
- `/api/v1/docs`
- `/api/v1/ping` (compat alias)

Root app also serves:
- `/` (marketing home)
- `/docs` (HTML docs)
- retro SEO landing pages (`/seo-audit-api`, `/website-scraper-api`, etc.)
- operational routes (`/health`, `/health/detailed`, `/metrics`, `/status`)

## 6. Endpoint Documentation

## 6.1 Analyze Endpoints

### `POST /api/v1/analyze`

Purpose:
- Run broad website analysis using the core analyzer pipeline.

Request body:

```json
{
  "url": "https://example.com",
  "options": {
    "screenshot": true,
    "use_browser": false,
    "refresh_cache": false
  }
}
```

Behavior:
- Validates `url` and `options`.
- Checks cache unless `refresh_cache=true`.
- Checks and consumes quota when user context exists.
- Adds user plan into options for downstream gating.
- Tracks domain analytics.

Response:
- Envelope response via `APIResponse.success`.
- `data` payload includes extraction and analysis signals from `app/services/analyzer.py`.
- Typical keys: `url`, `title`, `description`, `logo`, `favicon`, `emails`, `phones`, `socials`, `tech_stack`, `language`, `country_guess`, `schema_org`, `og_tags`, keywords, optional screenshot fields, and diagnostics.

### `POST /api/v1/analyze/tech`

Purpose:
- Detect stack technologies and foundational web languages.

Request body:

```json
{
  "url": "https://example.com",
  "options": {
    "use_browser": false
  }
}
```

Response (direct model):

```json
{
  "url": "https://example.com",
  "languages": ["HTML", "CSS", "JavaScript"],
  "technologies": ["CSS", "HTML", "JavaScript", "React", "Google Analytics"],
  "timestamp": 1776540000.0,
  "processing_time_ms": 321
}
```

Notes:
- `technologies` is a combined set that includes detected language labels.
- Language detection currently uses presence heuristics for HTML/CSS/JS signals.

### `OPTIONS /api/v1/analyze`

Purpose:
- Preflight compatibility endpoint.

Response:
- Empty object `{}`.

## 6.2 Extraction Endpoints

### `POST /api/v1/extract/emails`

Purpose:
- Extract deduplicated emails from a single page or deep crawl.

Request body:

```json
{
  "url": "https://example.com",
  "options": {
    "deep_search": false,
    "pages_limit": 10,
    "use_browser": false
  }
}
```

Plan gating:
- `deep_search` allowed only for plans: `pro`, `ultra`, `mega`.
- `use_browser` allowed only for plans: `pro`, `ultra`, `mega`.
- `pages_limit` upper bounds vary by plan when deep search is enabled.

Response (direct model):

```json
{
  "url": "https://example.com",
  "emails": ["info@example.com", "support@example.com"],
  "count": 2,
  "timestamp": 1776540000.0,
  "processing_time_ms": 850
}
```

### `POST /api/v1/extract/schema`

Purpose:
- Extract Schema.org plus Open Graph tags.

Request body:

```json
{
  "url": "https://example.com",
  "options": {
    "use_browser": false
  }
}
```

Response:

```json
{
  "url": "https://example.com",
  "schema_org": {"@type": "Organization"},
  "og_tags": {"title": "Example"},
  "timestamp": 1776540000.0,
  "processing_time_ms": 230
}
```

Notes:
- `schema_org` may be `null`.
- `og_tags` may be `null`.
- Route is now single-defined; duplicate-definition regression was removed.

### `POST /api/v1/extract/metadata`

Purpose:
- Extract consolidated metadata fields in one call.

Response:
- Direct model with:
  - `url`
  - `title` (nullable)
  - `description` (nullable)
  - `schema_org` (nullable)
  - `og_tags` (nullable)
  - `timestamp`
  - `processing_time_ms`

## 6.3 SEO Endpoints

### `POST /api/v1/seo/seo-audit`

Purpose:
- Perform weighted SEO scoring (`0..100`) with structured audit items.

Checks include:
- Title quality
- Meta description quality
- Heading hierarchy
- Image alt coverage
- Structured data presence
- Open Graph completeness
- Mobile viewport configuration
- Technical checks (HTTPS, canonical, indexing, URL format)

Request:

```json
{
  "url": "https://example.com",
  "options": {
    "use_browser": false
  }
}
```

Response:

```json
{
  "url": "https://example.com",
  "score": 78,
  "audit_items": [
    {
      "check": "Title",
      "passed": true,
      "score": 85,
      "message": "Good title length",
      "severity": "info"
    }
  ],
  "timestamp": 1776540000.0,
  "processing_time_ms": 1200
}
```

### `POST /api/v1/seo/broken-links`

Purpose:
- Parse links and return broken-link summary model.

Request:

```json
{
  "url": "https://example.com",
  "check_external": false,
  "options": {}
}
```

Response:
- `url`
- `total_links`
- `broken_links_count`
- `internal_links`
- `external_links`
- `broken_links` (array)
- `timestamp`
- `processing_time_ms`

Operational note:
- Current implementation emphasizes internal extraction/counting and structural reporting.

## 6.4 Health and Ops Endpoints

### `GET /api/v1/health/`

Returns:
- `status` (`healthy` or `degraded`)
- service metadata
- dependency status:
  - database
  - redis

### `GET /api/v1/health/ping`

Returns:

```json
{"status":"ok","message":"pong"}
```

### `GET|HEAD /api/v1/ping`

Compatibility alias:

```json
{"status":"ok","message":"pong"}
```

## 6.5 Analytics Endpoints

All analytics endpoints return envelope responses.

### `GET /api/v1/analytics/`

Query:
- `days` (int, `1..90`, default `7`)

Data includes:
- `usage_stats`
- `popular_domains`
- `performance_metrics`
- `generated_at`

### `GET /api/v1/analytics/performance`

Query:
- `days` (int, `1..90`, default `7`)

Data:
- Performance metric object from analytics service.

### `GET /api/v1/analytics/endpoints`

Query:
- `days` (int, `1..90`, default `7`)

Data:
- endpoint usage map and top endpoint list.

## 6.6 Account and Billing Endpoints

All routes below require authenticated user context (`get_current_user`).

Base prefix:
- `/api/v1/account`

### `GET /api/v1/account/subscription`
- Get active subscription details or free-tier fallback.

### `POST /api/v1/account/subscription/upgrade`

Request:

```json
{
  "plan": "pro",
  "billing_cycle": "monthly"
}
```

Valid plans:
- `free`
- `starter`
- `pro`
- `business`
- `enterprise`

### `POST /api/v1/account/subscription/cancel`
- Cancel active subscription and downgrade to free.

### `GET /api/v1/account/billing/invoices`
- List invoices.

### `GET /api/v1/account/billing/payment-methods`
- List payment methods.

### `POST /api/v1/account/billing/payment-methods`

Request:

```json
{
  "payment_method_id": "pm_123"
}
```

### `POST /api/v1/account/webhooks/stripe`
- Stripe event receiver and verification path.

### `GET /api/v1/account/account/billing-summary`
- Returns plan + quota + billing snapshot.
- This path currently includes duplicate `account` segment by implementation and is documented as-is.

## 6.7 Versioned Docs Route Aliases

Because docs router is mounted both at root and under `/api/v1/docs`, the following HTML routes also exist:
- `/api/v1/docs/`
- `/api/v1/docs/docs`
- `/api/v1/docs/seo-audit-api`
- `/api/v1/docs/website-scraper-api`
- `/api/v1/docs/email-extractor-api`
- `/api/v1/docs/tech-stack-detector-api`
- `/api/v1/docs/website-metadata-api`
- `/api/v1/docs/competitor-website-analysis-api`
- `/api/v1/docs/about-pageiq`
- `/api/v1/docs/pricing-plans`
- `/api/v1/docs/faq-page`
- `/api/v1/docs/guestbook`
- `/api/v1/docs/blog-archive`

## 7. Root Website Pages (Retro Marketing + SEO)

Current root pages:
- `/`
- `/docs`
- `/seo-audit-api`
- `/website-scraper-api`
- `/email-extractor-api`
- `/tech-stack-detector-api`
- `/website-metadata-api`
- `/competitor-website-analysis-api`
- `/about-pageiq`
- `/pricing-plans`
- `/faq-page`
- `/guestbook`
- `/blog-archive`

These pages are intentionally content-heavy and long-tail intent-oriented to support SEO growth through multiple entry points.

## 8. Common Error Cases

Typical failure classes you should handle:
- URL validation failures (`400` / `422` depending on validation layer)
- Fetch/parsing failures (`400`)
- Robots restrictions (`403`)
- Plan/feature gate restrictions (`403`)
- Quota/rate limiting (`429`)
- Internal processing errors (`500`)

For Pydantic field errors, parse response details for `type`, `loc`, and message context.

## 9. Integration Recommendations

- Normalize endpoint response style in your client library (envelope vs direct model).
- Store `request_id` when available for support/debugging.
- Apply retries with exponential backoff on transient `5xx`.
- Treat `403` as either authorization or feature-gate scenario and branch messaging accordingly.
- For batch-like workflows, keep extraction and analysis routes separated by purpose:
  - use `/analyze` for broad intelligence
  - use `/extract/*` when you need targeted payloads
  - use `/seo/*` for scoring and QA workflows

## 10. Quick cURL Examples

Analyze:

```bash
curl -X POST "https://pageiq.pompora.dev/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url":"https://example.com","options":{"screenshot":true}}'
```

Tech detection:

```bash
curl -X POST "https://pageiq.pompora.dev/api/v1/analyze/tech" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url":"https://example.com","options":{}}'
```

Email extraction:

```bash
curl -X POST "https://pageiq.pompora.dev/api/v1/extract/emails" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url":"https://example.com","options":{"deep_search":false}}'
```

SEO audit:

```bash
curl -X POST "https://pageiq.pompora.dev/api/v1/seo/seo-audit" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url":"https://example.com","options":{}}'
```

## 11. Change Tracking Notes

Recent implementation-level highlights reflected in this document:
- `/extract/schema` duplicate route definition removed, preventing `og_tags` missing-field server errors.
- `/analyze/tech` now includes explicit `languages` and merges languages into `technologies`.
- Root site and intent pages now include full retro content architecture for SEO strategy and multi-entry growth.

