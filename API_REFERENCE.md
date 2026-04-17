# PageIQ API Reference

**Base URL:** `https://pageiq.pompora.dev/api/v1`

**API Version:** 1.0.0

---

## Quick Start

### 1. Get an API Key

Send a POST request to get a test API key (for demo purposes):

```bash
curl -X POST https://pageiq.pompora.dev/api/v1/account/keys \
  -H "Content-Type: application/json" \
  -d '{"name": "my-app"}'
```

Response:
```json
{
  "id": 1,
  "name": "my-app",
  "key": "sk_live_abc123xyz789",
  "created_at": "2026-04-17T12:00:00Z"
}
```

### 2. Make Your First Request

Analyze any website:

```bash
curl -X POST https://pageiq.pompora.dev/api/v1/analyze \
  -H "Authorization: Bearer sk_live_abc123xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "options": {
      "screenshot": true,
      "extract_emails": true
    }
  }'
```

### 3. Check Your Quota

```bash
curl https://pageiq.pompora.dev/api/v1/account/quota \
  -H "Authorization: Bearer sk_live_abc123xyz789"
```

---

## Authentication

PageIQ uses API key authentication. All requests require the `Authorization` header.

**Header Format:**
```
Authorization: Bearer YOUR_API_KEY
```

**Anonymous Access:**

Some endpoints allow anonymous requests (no authentication required). These include:
- `GET /ping` - Health check
- `GET /` - Health status

For authenticated endpoints without a key, you'll receive a **401 Unauthorized** error.

---

## API Endpoints

### Health & Monitoring

#### GET `/`
Health check endpoint. Returns API status.

**Request:**
```bash
curl https://pageiq.pompora.dev/api/v1/
```

**Response:**
```json
{
  "status": "healthy",
  "service": "PageIQ API"
}
```

---

#### GET `/ping`
Simple ping for monitoring and uptime checks.

**Request:**
```bash
curl https://pageiq.pompora.dev/api/v1/ping
```

**Response:**
```json
{
  "status": "ok",
  "message": "pong"
}
```

---

### Website Analysis

#### POST `/analyze`
Analyze a website and return structured business intelligence.

**Request:**
```bash
curl -X POST https://pageiq.pompora.dev/api/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "options": {
      "screenshot": true,
      "extract_emails": true,
      "detect_technology": true,
      "detect_industry": true,
      "analyze_seo": true
    }
  }'
```

**Request Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | The website URL to analyze |
| `options` | object | No | Analysis options (see below) |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `screenshot` | boolean | false | Capture screenshot of the page |
| `extract_emails` | boolean | false | Extract email addresses |
| `detect_technology` | boolean | true | Detect tech stack (frameworks, tools) |
| `detect_industry` | boolean | true | Auto-detect industry classification |
| `analyze_seo` | boolean | false | Perform SEO analysis |
| `depth` | integer | 1 | Crawl depth (1-3) |

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "Example Domain. This domain is for use in examples...",
    "metadata": {
      "language": "en",
      "charset": "utf-8"
    },
    "technologies": [
      {
        "name": "jQuery",
        "category": "JavaScript Frameworks",
        "confidence": 95
      }
    ],
    "industry": "Technology",
    "emails": [
      "info@example.com",
      "support@example.com"
    ],
    "screenshot_url": "/screenshots/abc123.png",
    "seo": {
      "title_length": 14,
      "description_length": 74,
      "h1_count": 1,
      "images_without_alt": 5
    }
  },
  "request_id": "req_abc123xyz",
  "processing_time_ms": 2450,
  "quota_remaining": 999
}
```

**Status Codes:**
- `200` - Analysis successful
- `400` - Invalid URL or options
- `401` - Unauthorized (invalid/missing API key)
- `403` - Robots.txt forbids crawling
- `429` - Rate limit exceeded
- `500` - Server error

---

#### POST `/analyze` (Batch)
Analyze multiple websites in one request.

**Request:**
```bash
curl -X POST https://pageiq.pompora.dev/api/v1/batch-analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com",
      "https://example.org"
    ],
    "options": {
      "screenshot": true
    }
  }'
```

**Response:**
```json
{
  "batch_id": "batch_abc123",
  "status": "processing",
  "total": 2,
  "completed": 0,
  "results": []
}
```

---

### Data Extraction

#### POST `/extract/emails`
Extract email addresses from a webpage.

**Request:**
```bash
curl -X POST https://pageiq.pompora.dev/api/v1/extract/emails \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "options": {}
  }'
```

**Response:**
```json
{
  "url": "https://example.com",
  "emails": [
    "info@example.com",
    "support@example.com",
    "sales@example.com"
  ],
  "count": 3,
  "timestamp": 1713355200.123,
  "processing_time_ms": 450
}
```

---

### Analytics

#### GET `/analytics/summary`
Get analytics summary of your API usage.

**Request:**
```bash
curl https://pageiq.pompora.dev/api/v1/analytics/summary \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "period": "30d",
  "requests_total": 5432,
  "requests_today": 245,
  "average_response_time_ms": 1250,
  "most_analyzed_domain": "example.com",
  "error_rate": 0.02
}
```

---

### Account Management

#### GET `/account/quota`
Check your API quota and usage.

**Request:**
```bash
curl https://pageiq.pompora.dev/api/v1/account/quota \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "plan": "pro",
  "quota_limit": 10000,
  "quota_used": 2345,
  "quota_remaining": 7655,
  "reset_date": "2026-05-17T00:00:00Z",
  "percentage_used": 23.45
}
```

---

#### GET `/account/keys`
List all API keys for your account.

**Request:**
```bash
curl https://pageiq.pompora.dev/api/v1/account/keys \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "keys": [
    {
      "id": 1,
      "name": "my-app",
      "prefix": "sk_live_abc123",
      "created_at": "2026-04-17T12:00:00Z",
      "last_used": "2026-04-17T14:30:00Z",
      "revoked": false
    }
  ]
}
```

---

#### POST `/account/keys`
Create a new API key.

**Request:**
```bash
curl -X POST https://pageiq.pompora.dev/api/v1/account/keys \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-server"
  }'
```

**Response:**
```json
{
  "id": 2,
  "name": "production-server",
  "key": "sk_live_xyz789abc123",
  "created_at": "2026-04-17T15:00:00Z"
}
```

**Note:** The full API key is only returned once. Store it securely!

---

#### DELETE `/account/keys/{key_id}`
Revoke an API key.

**Request:**
```bash
curl -X DELETE https://pageiq.pompora.dev/api/v1/account/keys/1 \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "message": "API key revoked"
}
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "request_id": "req_abc123xyz"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|------------|-------------|
| `INVALID_URL` | 400 | URL is malformed or invalid |
| `ROBOTS_FORBIDDEN` | 403 | Robots.txt forbids crawling |
| `QUOTA_EXCEEDED` | 429 | Monthly API quota exceeded |
| `INVALID_API_KEY` | 401 | API key is invalid or expired |
| `NOT_FOUND` | 404 | Resource not found |
| `SERVER_ERROR` | 500 | Internal server error |

---

## Rate Limiting

PageIQ uses rate limiting to ensure fair access for all users.

**Limits by Plan:**

| Plan | Requests/Min | Requests/Day | Requests/Month |
|------|-------------|------------|----------------|
| Free | 10 | 100 | 1,000 |
| Pro | 60 | 10,000 | 100,000 |
| Enterprise | Unlimited | Unlimited | Unlimited |

**Headers:**

Each response includes rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1713355800
```

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response.

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```javascript
fetch('https://pageiq.pompora.dev/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://example.com'
  })
})
.then(response => {
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
})
.catch(error => console.error('Error:', error));
```

### 2. Batch Processing

Use batch endpoints for multiple URLs to save quota:

```bash
curl -X POST https://pageiq.pompora.dev/api/v1/batch-analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"urls": ["url1", "url2", "url3"]}'
```

### 3. Monitor Quota

Check quota regularly to avoid exceeding limits:

```bash
curl https://pageiq.pompora.dev/api/v1/account/quota \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 4. Caching

Cache results when analyzing the same URL multiple times:

```javascript
const cache = new Map();

async function analyzeURL(url) {
  if (cache.has(url)) {
    return cache.get(url);
  }
  
  const result = await fetch(/* ... */);
  cache.set(url, result);
  return result;
}
```

### 5. Timeouts

Set appropriate timeouts for API calls:

```javascript
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 30000); // 30 seconds

fetch('https://pageiq.pompora.dev/api/v1/analyze', {
  signal: controller.signal
})
.finally(() => clearTimeout(timeout));
```

---

## Support

- **Documentation:** https://pageiq.pompora.dev/docs
- **Email:** support@pompora.dev
- **Issues:** https://github.com/mitrashkov/pageiq/issues

---

## Changelog

### v1.0.0 (2026-04-17)
- Initial API release
- Website analysis
- Email extraction
- Technology detection
- Industry classification
- API key management
- Rate limiting

---
