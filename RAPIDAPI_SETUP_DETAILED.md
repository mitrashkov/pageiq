# 🚀 PageIQ RapidAPI: The Ultimate Configuration Guide (Every Step)

This is the **COMPLETE** guide for your RapidAPI dashboard. Do not skip any field. Follow this exactly to get a 5-star developer experience.

---

## 🟢 1. General Settings (Definition -> General)

- **Name:** `PageIQ - Website Intelligence & Extraction`
- **Description:** `Turn any URL into structured business data. Extract tech stack, professional emails, metadata, SEO audits, and social links with enterprise-grade reliability.`
- **Category:** `Data` or `Tools`
- **Image:** Upload your logo here.
- **Website:** `https://pageiq.pompora.dev`

---

## 🟡 2. Base URL (Definition -> Security)

- **Base URL:** `https://pageiq.pompora.dev/api/v1`
- **Proxy Secret:** Leave this for now if you haven't set it in Render, but eventually, copy the secret from this page and add `RAPIDAPI_PROXY_SECRET=your_secret` to Render.

---

## 🔴 3. ENDPOINTS SETUP (The "Messy" Part)

For **EVERY** endpoint below, follow these sub-steps in the **Endpoints** tab:

### 🔹 Endpoint 1: Analyze Website
- **Name:** `Analyze Website`
- **Method:** `POST`
- **Path:** `/analyze`
- **Description:** `Deep analysis of any URL. Returns tech stack, emails, social links, and business metadata.`
- **HEADERS (IMPORTANT):**
    - Click **Add Header**
    - Name: `Content-Type`
    - Default Value: `application/json`
- **BODY (The "JSON" Option):**
    - Scroll to **Request Body**.
    - **This is where you choose JSON.**
    - Click **Add Payload**.
    - Set Name to `body`.
    - Set Description to `Analysis options`.
    - **IMPORTANT:** Paste this into the **Example Value**:
      ```json
      {
        "url": "https://example.com",
        "options": {
          "screenshot": true,
          "use_browser": true
        }
      }
      ```

### 🔹 Endpoint 2: Extract Emails
- **Name:** `Extract Emails`
- **Method:** `POST`
- **Path:** `/extract/emails`
- **Description:** `Scans a webpage specifically for professional email addresses.`
- **HEADERS:** `Content-Type: application/json`
- **BODY:**
    - Click **Add Payload**.
    - Example Value:
      ```json
      {
        "url": "https://example.com/contact"
      }
      ```

### 🔹 Endpoint 3: SEO Audit
- **Name:** `SEO Audit`
- **Method:** `POST`
- **Path:** `/seo/seo-audit`
- **Description:** `Technical SEO check for titles, meta tags, and mobile readiness.`
- **HEADERS:** `Content-Type: application/json`
- **BODY:**
    - Example Value:
      ```json
      {
        "url": "https://example.com"
      }
      ```

---

## 🔵 4. PARAMETERS & TYPES (The "10 More Things")

When adding parameters (like in the Body payload):
1. **Type:** Choose `String` for the URL.
2. **Required:** Set to `Yes`.
3. **Description:** `The target website URL (e.g. https://google.com)`

---

## ⚪ 5. TRANSFORMATIONS (Optional but Pro)

If you want to hide our headers from users:
1. Go to **Transformations**.
2. Add a transformation to **Strip Headers**.
3. Strip `x-rapidapi-proxy-secret` and `Authorization`.

---

## 🛠 Troubleshooting Render "502/Network Error"

If you see "Failed to fetch":
1. **Wait 2 minutes:** Render's free tier sleeps. The first request takes 60 seconds to "wake up".
2. **CORS:** I have already set `allow_origins=["*"]` in the code. This is the #1 fix for "Failed to fetch".
3. **Redis:** I have fixed the Redis crash. Your app will now start even if Redis is missing.
4. **Logs:** Go to Render Dashboard -> Logs. If you see "Exited with status 1", look at the error. If you see "Uvicorn running on http://0.0.0.0:10000", it's working!

---

## 🚀 FINAL COMMANDS TO DEPLOY

Run these in your terminal now:
```bash
git add .
git commit -m "Final production fixes: optional redis, relaxed rapidapi auth, and ultimate docs"
git push origin main
```
Render will automatically see this and deploy. Your API will be live at:
`https://pageiq.pompora.dev/api/v1`
