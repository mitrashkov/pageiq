# RapidAPI Integration Guide

PageIQ is ready for RapidAPI Marketplace! Here's how to list and configure it.

---

## What is RapidAPI?

RapidAPI is a marketplace where developers discover and use APIs. It handles billing, authentication, and provides SDKs for multiple languages.

**Key Benefits:**
- ✅ Automatic billing through RapidAPI (no Stripe needed)
- ✅ Massive developer audience
- ✅ Built-in SDK generation
- ✅ Usage analytics and monetization

---

## Step 1: Sign Up / Login to RapidAPI

1. Go to: https://rapidapi.com
2. Click **"Sign Up"** (or login if you have an account)
3. Complete profile setup

---

## Step 2: Create Your API on RapidAPI

1. Go to Dashboard: https://rapidapi.com/developer/dashboard
2. Click **"Add New"** → **"API"**
3. Fill in the form:

| Field | Value |
|-------|-------|
| **API Name** | `PageIQ` |
| **Description** | Website Intelligence API - turn any URL into structured business data |
| **Category** | Web Tools / API Tools |
| **API Gateway** | REST |
| **Requires Authentication** | Yes |
| **Base URL** | `https://pageiq.pompora.dev/api/v1` |

4. Click **"Create API"**

---

## Step 3: Add API Endpoints

For each endpoint, you'll add details. Start with the main ones:

### Endpoint 1: Analyze Website

- **Method:** POST
- **Path:** `/analyze`
- **Name:** Analyze Website
- **Description:** Analyze a website and return structured business data

**Request Parameters:**
```json
{
  "url": "string (required)",
  "options": {
    "screenshot": "boolean",
    "extract_emails": "boolean",
    "detect_technology": "boolean",
    "detect_industry": "boolean",
    "analyze_seo": "boolean"
  }
}
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example",
    "description": "Example Domain",
    "technologies": [],
    "industry": "Technology",
    "emails": [],
    "seo": {}
  },
  "request_id": "req_abc123",
  "processing_time_ms": 2450,
  "quota_remaining": 999
}
```

### Endpoint 2: Extract Emails

- **Method:** POST
- **Path:** `/extract/emails`
- **Name:** Extract Email Addresses
- **Description:** Extract email addresses from a webpage

### Endpoint 3: Get Quota

- **Method:** GET
- **Path:** `/account/quota`
- **Name:** Get API Quota
- **Description:** Check your current API quota and usage

### Endpoint 4: Health Check

- **Method:** GET
- **Path:** `/ping`
- **Name:** Health Check
- **Description:** Simple endpoint to verify API is running

---

## Step 4: Configure Authentication

### Method: API Key

1. In RapidAPI dashboard, go to **"Authentication"**
2. Select **"API Key"** type
3. Configure:
   - **Location:** Header
   - **Header Name:** `Authorization`
   - **Format:** `Bearer YOUR_API_KEY`
   - **Name to display in docs:** "API Key"

4. Provide sample:
   ```
   Bearer sk_live_abc123xyz789
   ```

---

## Step 5: Set Up Pricing & Plans

### Free Plan (Freemium)
- **Requests/Month:** 1,000
- **Price:** Free
- **Features:** Basic analysis, no screenshots

### Pro Plan
- **Requests/Month:** 100,000
- **Price:** $29/month or $49/month (your choice)
- **Features:** Full analysis, screenshots, batch requests

### Enterprise Plan
- **Requests/Month:** Unlimited
- **Price:** Custom (contact sales)

**To Configure:**

1. Go to **"Pricing"** section
2. Click **"Add Plan"**
3. Set tier name, request limit, price
4. Click **"Save"**

---

## Step 6: Test Integration

### Using RapidAPI Testing Console

1. In your API dashboard, go to **"Testing"** section
2. Select an endpoint (e.g., `/ping`)
3. Click **"Test"**
4. RapidAPI will make a request to your API
5. You should see response in console

**Expected Response:**
```json
{
  "status": "ok",
  "message": "pong"
}
```

### Test with cURL

RapidAPI provides cURL examples. Example:

```bash
curl --get --include 'https://pageiq.p.rapidapi.com/api/v1/ping' \
  -H 'x-rapidapi-key: YOUR_RAPIDAPI_KEY' \
  -H 'x-rapidapi-host: pageiq.p.rapidapi.com'
```

---

## Step 7: Upload Documentation

1. Go to **"Documentation"** section
2. Add markdown-formatted documentation
3. Include:
   - Overview of what your API does
   - Getting started guide
   - Endpoint reference
   - Code examples (JavaScript, Python, etc.)

**Sample Documentation Template:**

```markdown
# PageIQ API

Website Intelligence API that turns any URL into structured business data.

## Getting Started

1. Get an API key
2. Make a POST request to `/analyze` with a URL
3. Receive structured website data

## Endpoints

### POST /analyze

Analyze any website.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "data": { /* ... */ }
}
```

### GET /account/quota

Check your quota.

**Response:**
```json
{
  "plan": "pro",
  "quota_remaining": 9975
}
```
```

---

## Step 8: Publish Your API

1. Go to **"Settings"** → **"Publish"**
2. Select visibility:
   - **Private:** Only you can see
   - **Public:** Everyone can see and subscribe
3. Click **"Publish"**

---

## Step 9: Monitor & Manage

### Dashboard Features

After publishing, you can:

- **View Usage:** See analytics, requests, errors
- **Manage Subscribers:** See who's using your API
- **View Revenue:** How much you're earning
- **Support Tickets:** Customer inquiries
- **API Logs:** All requests to your API

### Monitoring URL

Go to: https://rapidapi.com/developer/dashboard

---

## RapidAPI SDK Generation

RapidAPI automatically generates SDKs for:

- ✅ JavaScript/Node.js
- ✅ Python
- ✅ Java
- ✅ Go
- ✅ PHP
- ✅ Swift
- ✅ Ruby

Example (Generated JavaScript):

```javascript
const rapidapi = require('rapidapi-connect');

const api = new rapidapi.Client();
api.authenticate('YOUR_RAPIDAPI_KEY');

api.callAsync('https://pageiq.p.rapidapi.com/api/v1/analyze', 'POST', {
  url: 'https://example.com'
})
.then(output => console.log(output))
.catch(error => console.log(error));
```

---

## API Host on RapidAPI

Once published, your API will be available at:

```
https://pageiq.p.rapidapi.com/api/v1
```

**Note:** `p.rapidapi.com` is RapidAPI's proxy. Your actual API at `pageiq.pompora.dev` remains unchanged.

---

## Billing & Revenue Share

- **RapidAPI Rate:** 30% RapidAPI + 70% to you
- **Payouts:** Monthly via PayPal/Stripe
- **Minimum:** $1 to payout
- **Frequency:** Monthly on the 20th

---

## Troubleshooting

### "API is not responding"

Check:
1. Is your API running? Test at `https://pageiq.pompora.dev/api/v1/ping`
2. Is the base URL correct in RapidAPI settings?
3. Are your endpoints accessible?

### "Authentication failing"

Check:
1. Is the Authorization header format correct? (`Bearer YOUR_KEY`)
2. Are you passing the actual API key (not placeholder)?

### "Subscribers can't access my API"

Check:
1. Is the API "Published" (not in draft)?
2. Did you set a pricing tier?
3. Are they on a valid plan?

---

## What Happens When Someone Uses Your API?

1. Developer subscribes to a plan on RapidAPI
2. RapidAPI gives them a special API key
3. They call your API through RapidAPI's proxy
4. RapidAPI forwards request to your actual API
5. Your API responds normally
6. RapidAPI tracks usage and billing
7. You get paid monthly for requests used

---

## Next Steps

1. ✅ Create API on RapidAPI
2. ✅ Add endpoints
3. ✅ Configure pricing
4. ✅ Test with RapidAPI console
5. ✅ Publish to marketplace
6. ✅ Monitor analytics

---

## Support

- **RapidAPI Help:** https://rapidapi.com/help
- **PageIQ Support:** support@pompora.dev
- **GitHub Issues:** https://github.com/mitrashkov/pageiq/issues

---
