# PageIQ API Documentation

Comprehensive, current documentation for all active routes in this codebase.

## Base URLs
- Production app root: `https://pageiq.pompora.dev`
- API v1 base: `https://pageiq.pompora.dev/api/v1`

## Authentication
- Protected endpoints accept API key auth (handled by middleware/dependencies).
- Common header format:

```http
X-API-Key: YOUR_API_KEY
```

- Some account/billing endpoints require authenticated user context via `get_current_user`.

## Response Formats

### Standard Success Envelope (`APIResponse.success`)

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

### Standard Error Envelope (`APIResponse.error`)

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

### Direct Model Responses
- Some endpoints (notably `extract/*`, `seo/*`, and `health/*`) return model-shaped JSON directly instead of the success envelope.

## Public Website Pages (SEO + Docs)

### `GET /`
- Landing page.
- Hero:
  - `Turn Any Website Into Actionable Business Data`
  - Subtext: `Extract SEO score, tech stack, metadata, verified emails, socials, and hidden business intelligence from any URL.`
  - CTA: `Try on RapidAPI`
- Includes internal use-case links for SEO pages.

### `GET /docs`
- HTML documentation page.

### Intent Landing Pages
- `GET /seo-audit-api`
- `GET /website-scraper-api`
- `GET /email-extractor-api`
- `GET /tech-stack-detector-api`
- `GET /website-metadata-api`
- `GET /competitor-website-analysis-api`

These pages are multiple search-intent entry points for SEO growth.

## App-Level Operational Endpoints

### `GET /health`
- Basic service health.

### `GET /health/detailed`
- Dependency checks (`database`, `redis`, `application`).

### `GET /metrics`
- Prometheus-style metrics output.

### `GET /status`
- Operational status + metrics summary.

## API v1 Endpoints

## Health

### `GET /api/v1/health/`
- Comprehensive health check.
- Returns dependency states for database and redis.

### `GET /api/v1/health/ping`
- Returns:

```json
{"status":"ok","message":"pong"}
```

### `GET|HEAD /api/v1/ping`
- Compatibility ping alias.

## Analyze

### `POST /api/v1/analyze`
Analyze a URL and return structured website intelligence.

Request:

```json
{
  "url": "https://example.com",
  "options": {
    "screenshot": true,
    "use_browser": false
  }
}
```

Response:
- Standard success envelope (`APIResponse.success`)
- `data` is produced by the core analyzer pipeline and includes fields such as:
  - `url`, `title`, `description`, `logo`, `favicon`
  - `emails`, `phones`, `socials`
  - `tech_stack`, `industry_guess`, `language`, `country_guess`
  - `keywords`, `schema_org`, `og_tags`
  - optional screenshot and diagnostics fields

Notes:
- Uses cache when `options.refresh_cache` is not set.
- Performs quota checks and consumption when user context is present.

### `POST /api/v1/analyze/tech`
Detect technologies and website languages.

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
  "languages": ["HTML", "CSS", "JavaScript"],
  "technologies": ["CSS", "HTML", "JavaScript", "React"],
  "timestamp": 1776540000.0,
  "processing_time_ms": 321
}
```

### `OPTIONS /api/v1/analyze`
- Lightweight preflight response.

## Analytics

### `GET /api/v1/analytics/`
Query params:
- `days` (int, optional, `1..90`, default `7`)

Returns usage stats, popular domains, performance metrics via success envelope.

### `GET /api/v1/analytics/performance`
Query params:
- `days` (int, optional, `1..90`, default `7`)

Returns detailed performance metrics via success envelope.

### `GET /api/v1/analytics/endpoints`
Query params:
- `days` (int, optional, `1..90`, default `7`)

Returns endpoint usage breakdown via success envelope.

## Extract

### `POST /api/v1/extract/emails`
Extract deduplicated email addresses from a page or deep crawl.

Request:

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

Key options and plan gating:
- `deep_search`: Premium feature (`pro`, `ultra`, `mega`)
- `pages_limit`: plan-based cap when deep search is enabled
- `use_browser`: Premium feature (`pro`, `ultra`, `mega`)

Response:
- Direct model response with:
  - `url`, `emails`, `count`, `timestamp`, `processing_time_ms`

### `POST /api/v1/extract/schema`
Extract Schema.org and Open Graph.

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
  "schema_org": {"@type":"Organization"},
  "og_tags": {"title":"Example"},
  "timestamp": 1776540000.0,
  "processing_time_ms": 210
}
```

Notes:
- `schema_org` and `og_tags` may be `null` when not found.

### `POST /api/v1/extract/metadata`
Extract combined metadata in one call.

Response fields:
- `url`
- `title`
- `description`
- `schema_org`
- `og_tags`
- `timestamp`
- `processing_time_ms`

## SEO

### `POST /api/v1/seo/seo-audit`
Runs weighted SEO checks and returns score `0..100`.

Includes checks like:
- title
- meta description
- heading hierarchy
- image alt coverage
- structured data
- Open Graph
- mobile viewport
- technical checks (HTTPS, canonical, indexing, URL structure)

Response:
- Direct model response with:
  - `url`, `score`, `audit_items[]`, `timestamp`, `processing_time_ms`

### `POST /api/v1/seo/broken-links`
Extracts links and reports counts and broken links.

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
- `broken_links`
- `timestamp`
- `processing_time_ms`

## Billing and Account

All routes below are under `/api/v1/account` and require authenticated user context.

### `GET /api/v1/account/subscription`
- Get current subscription details.

### `POST /api/v1/account/subscription/upgrade`
- Upgrade plan.

Request:

```json
{
  "plan": "pro",
  "billing_cycle": "monthly"
}
```

### `POST /api/v1/account/subscription/cancel`
- Cancel active subscription and downgrade.

### `GET /api/v1/account/billing/invoices`
- List invoices.

### `GET /api/v1/account/billing/payment-methods`
- List payment methods.

### `POST /api/v1/account/billing/payment-methods`
- Add payment method.

Request:

```json
{
  "payment_method_id": "pm_123"
}
```

### `POST /api/v1/account/webhooks/stripe`
- Stripe webhook receiver.

### `GET /api/v1/account/account/billing-summary`
- Current implemented route path for billing summary.

Note:
- The duplicated `account` segment is present in the current route definition and is documented here exactly as implemented.

## Versioned Documentation Aliases

Because docs router is mounted both at app root and under `/api/v1/docs`, these are also available:

- `GET /api/v1/docs/`
- `GET /api/v1/docs/docs`
- `GET /api/v1/docs/seo-audit-api`
- `GET /api/v1/docs/website-scraper-api`
- `GET /api/v1/docs/email-extractor-api`
- `GET /api/v1/docs/tech-stack-detector-api`
- `GET /api/v1/docs/website-metadata-api`
- `GET /api/v1/docs/competitor-website-analysis-api`

## Common HTTP Status Codes
- `200` success
- `400` bad request / fetch/parse failures / invalid payloads
- `401` unauthorized
- `403` forbidden (plan restrictions, robots blocks, invalid signatures)
- `404` not found
- `429` rate limit exceeded
- `500` internal server error
