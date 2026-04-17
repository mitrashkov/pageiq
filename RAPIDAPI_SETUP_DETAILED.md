# RapidAPI Integration & Configuration Guide for PageIQ

This guide provides a comprehensive walkthrough for integrating the PageIQ API with RapidAPI. It includes every detail needed to set up endpoints, configure the proxy, and provide a world-class developer experience.

## 1. RapidAPI Configuration

### Proxy Authentication
PageIQ uses a **Proxy Secret** to verify that requests are genuinely coming from RapidAPI.

1. In your RapidAPI Provider Dashboard, go to **Definition** -> **Security**.
2. Find the **Proxy Secret** section.
3. Copy the secret and add it to your Render environment variables as:
   `RAPIDAPI_PROXY_SECRET=your_rapidapi_proxy_secret`

### API Host
Your API is hosted at: `https://pageiq.pompora.dev/api/v1`

---

## 2. API Endpoints Reference

### **Endpoint 1: Analyze Website (POST)**
*The core engine that turns any URL into structured business intelligence.*

- **Path:** `/analyze`
- **Description:** Performs a deep analysis of a website, including metadata, tech stack, social links, contact info, and business category.
- **Request Body (JSON):**
  ```json
  {
    "url": "https://example.com",
    "options": {
      "screenshot": true,
      "use_browser": true
    }
  }
  ```
- **Response Example:**
  ```json
  {
    "success": true,
    "data": {
      "title": "Example Domain",
      "description": "This domain is for use in illustrative examples...",
      "tech_stack": ["Nginx", "OpenSSL"],
      "social_links": ["https://twitter.com/example"],
      "emails": ["info@example.com"],
      "industry": "Technology",
      "screenshot_url": "https://pageiq.pompora.dev/screenshots/..."
    }
  }
  ```

### **Endpoint 2: Extract Emails (POST)**
*Extract and validate all professional email addresses found on a page.*

- **Path:** `/extract/emails`
- **Description:** Scans the webpage for email patterns in text, footers, and contact forms. Returns unique, validated emails.
- **Request Body (JSON):**
  ```json
  {
    "url": "https://example.com/contact"
  }
  ```

### **Endpoint 3: SEO Audit (POST)**
*Perform a comprehensive technical SEO audit of any webpage.*

- **Path:** `/seo/seo-audit`
- **Description:** Checks titles, meta descriptions, headings (H1-H6), image alt tags, and mobile-friendliness.
- **Request Body (JSON):**
  ```json
  {
    "url": "https://example.com"
  }
  ```

### **Endpoint 4: Batch Analyze (POST)**
*Process multiple websites in a single asynchronous request.*

- **Path:** `/batch-analyze`
- **Description:** Submit a list of URLs for analysis. Returns a `batch_id` to track progress.
- **Request Body (JSON):**
  ```json
  {
    "urls": ["https://site1.com", "https://site2.com"]
  }
  ```

### **Endpoint 5: Health Check (GET)**
*Monitor the status of the API and its dependencies.*

- **Path:** `/health`
- **Description:** Returns the current health of the API, database, and Redis.
- **Response:**
  ```json
  {
    "status": "healthy",
    "service": "PageIQ API",
    "dependencies": {
      "database": "healthy",
      "redis": "healthy"
    }
  }
  ```

---

## 3. RapidAPI Dashboard Setup

### Endpoints Tab
For every endpoint listed above, add them to the **Endpoints** tab in RapidAPI:

1. **Name:** Give it a clear name (e.g., "Analyze Website").
2. **Method:** Set to `POST`.
3. **URL:** Use the relative path (e.g., `/analyze`).
4. **Description:** Use the descriptions provided above.
5. **Payload:** Provide the example JSON from above in the **Request Body** section.

### Pricing Plans
RapidAPI handles the billing. You should align your RapidAPI plans with the `plan` header we handle:
- **Free:** 100 requests/month
- **Basic:** 1,000 requests/month
- **Pro:** 10,000 requests/month
- **Business:** 50,000 requests/month

---

## 4. Enabling Interactive Tests & Client-Side Access

To ensure developers can test the API directly from the RapidAPI UI without CORS issues:

1. **Base URL:** Ensure your Base URL in RapidAPI is set to `https://pageiq.pompora.dev/api/v1`.
2. **CORS:** We have already optimized the server to allow all origins (`*`) and all common RapidAPI headers.
3. **Response Headers:** The API is configured to expose all headers to the client, ensuring RapidAPI's testing tab can display full request/response info.

---

## 5. Troubleshooting Render (CORS & 502)

If you see a **502 CORS Error** or **Failed to fetch** on Render:

1. **Check ALLOWED_HOSTS:** Ensure `ALLOWED_HOSTS=["*"]` is set (we already enabled this).
2. **Proxy Headers:** We've enabled `--proxy-headers` in `start.sh` so Render/Cloudflare/RapidAPI can pass the correct IP and Protocol.
3. **CORS Headers:** We've relaxed the `Cross-Origin-Resource-Policy` to `cross-origin` in `app/core/security_headers.py`.
4. **Environment Variables:** Make sure you've added `RAPIDAPI_PROXY_SECRET` to Render dashboard.

## 5. Deployment Checklist
1. [ ] Push this code to GitHub.
2. [ ] Render will auto-deploy.
3. [ ] Verify health at `https://pageiq.pompora.dev/api/v1/health`.
4. [ ] Test the `/analyze` endpoint from the RapidAPI "Test Endpoint" button.
