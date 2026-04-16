# PageIQ API Documentation

## Overview
PageIQ provides a simple REST API to extract structured business intelligence from any website URL.

## Authentication
All API requests require an API key sent in the Authorization header:
```
Authorization: Bearer your-api-key-here
```

## Rate Limits
- Free tier: 100 requests/month
- Basic: 5,000 requests/month
- Pro: 50,000 requests/month
- Business: 500,000 requests/month

## Endpoints

### POST /api/v1/analyze
Analyze a website and return structured data.

**Request Body:**
```json
{
  "url": "https://example.com",
  "options": {
    "screenshot": true,
    "timeout": 30
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example Company",
    "description": "Leading provider...",
    "emails": ["info@example.com"],
    "socials": {
      "linkedin": "https://linkedin.com/company/example"
    }
  },
  "request_id": "req_123",
  "quota_remaining": 99
}
```

## Error Codes
- `400`: Bad Request
- `401`: Unauthorized
- `402`: Payment Required
- `429`: Too Many Requests
- `500`: Internal Server Error