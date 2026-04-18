# 🚀 PageIQ RapidAPI: The ULTIMATE Visual Guide (Step-by-Step)

Follow this guide EXACTLY. I have mapped every field to the RapidAPI dashboard.

---

## � STEP 1: Security (Definition -> Security)

- **Base URL:** `https://pageiq.pompora.dev/api/v1`
- **Proxy Secret:** (Copy this secret and add `RAPIDAPI_PROXY_SECRET=your_secret` to Render environment variables later).

---

## 🔴 STEP 2: ENDPOINTS (The "Fields" to Fill)

For each endpoint below, click **"Add Endpoint"** in the **Endpoints** tab and fill the fields as shown:

### 🔹 1. Analyze Website
- **Method:** `POST`
- **Path:** `/analyze`
- **Name:** `Analyze Website`
- **Description:** `Deep intelligence extraction: tech stack, emails, social links, and business metadata.`
- **Headers:** Add `Content-Type` with value `application/json`.
- **Body (Request Body Tab):**
    - **Media Type:** `application/json`
    - **Payload Name:** `body`
    - **Example Value:**
      ```json
      {
        "url": "https://example.com",
        "options": {
          "screenshot": true,
          "use_browser": true
        }
      }
      ```

### 🔹 2. Extract Emails
- **Method:** `POST`
- **Path:** `/extract/emails`
- **Name:** `Extract Emails`
- **Description:** `Professional-grade email extraction. Features AI-powered deep site crawling for massive lead generation.`
- **Headers:** Add `Content-Type` with value `application/json`.
- **Body (Request Body Tab):**
    - **Media Type:** `application/json`
    - **Payload Name:** `body` (This MUST be `body` in the RapidAPI dashboard field)
    - **Example Value:**
      ```json
      {
        "url": "https://example.com",
        "options": {
          "deep_search": true,
          "pages_limit": 100
        }
      }
      ```
      *(Note: `deep_search` is a Premium feature. PRO: 50 pgs, ULTRA: 150 pgs, MEGA: 500 pgs)*

### 🔹 3. Website Analysis (Advanced)
- **Method:** `POST`
- **Path:** `/analyze`
- **Name:** `Deep Analysis`
- **Description:** `Full technical and business intelligence. Includes JS Rendering and HD Screenshots for ULTRA/MEGA users.`
- **Body:**
      ```json
      {
        "url": "https://example.com",
        "options": {
          "use_browser": true,
          "screenshot": true
        }
      }
      ```

### 🔹 3. SEO Audit
- **Method:** `POST`
- **Path:** `/seo/seo-audit`
- **Name:** `SEO Audit`
- **Description:** `Complete technical SEO report: titles, meta tags, mobile readiness, and structured data.`
- **Headers:** Add `Content-Type` with value `application/json`.
- **Body:**
    - **Payload Name:** `body`
    - **Example Value:**
      ```json
      {
        "url": "https://example.com"
      }
      ```

### � 4. Broken Links Detector
- **Method:** `POST`
- **Path:** `/seo/broken-links`
- **Name:** `Broken Links Detector`
- **Description:** `Identify broken internal and external links on any webpage.`
- **Headers:** Add `Content-Type` with value `application/json`.
- **Body:**
    - **Payload Name:** `body`
    - **Example Value:**
      ```json
      {
        "url": "https://example.com",
        "check_external": true
      }
      ```

### 🔹 5. Batch Analyze
- **Method:** `POST`
- **Path:** `/batch-analyze`
- **Name:** `Batch Analyze`
- **Description:** `Submit multiple URLs for asynchronous analysis. Returns a batch_id.`
- **Headers:** Add `Content-Type` with value `application/json`.
- **Body:**
    - **Payload Name:** `body`
    - **Example Value:**
      ```json
      {
        "urls": ["https://site1.com", "https://site2.com"]
      }
      ```

### 🔹 6. API Health Check
- **Method:** `GET`
- **Path:** `/health`
- **Name:** `System Health`
- **Description:** `Check API, Database, and Redis connectivity status.`
- **Headers:** None needed.
- **Body:** None needed.

---

## 🛠 Solving the "404 Not Found" Error

If you get `message: "Endpoint does not exist"`:
1. **Check Base URL:** It MUST be `https://pageiq.pompora.dev/api/v1`.
2. **Leading Slashes:** Ensure your paths in RapidAPI start with `/` (e.g., `/analyze`).
3. **Wait for Deploy:** I am pushing the fixes NOW. Render takes 1 minute to update.

---

## 🚀 PUSHING TO GITHUB...

Run these commands in your terminal to sync with Render:
```bash
git add .
git commit -m "Fix 404 routing, SQLAlchemy 2.0 health check, and enhanced visual guide"
git push origin main
```
Render will auto-deploy. Check `https://pageiq.pompora.dev/api/v1/health` in 1 minute.
