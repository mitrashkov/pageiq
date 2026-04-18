# /extract/emails

**Method:** POST

**Description:**
Extract email addresses from a webpage or an entire website. Returns validated, unique email addresses.

**Request Body:**
- `url` (string, required): Website URL to extract emails from.
- `options` (object, optional): Extraction options.
- `options.deep_search` (bool): If true, crawls the website to find emails on multiple pages (default: false). **Available on PRO, ULTRA, and MEGA plans.**
- `options.pages_limit` (int): Maximum pages to crawl. Base cap is 20; higher limits are plan-gated when `deep_search=true`.
- `options.use_browser` (bool): Enables browser rendering for JS-heavy sites (PRO/ULTRA/MEGA only).

**Response:**
- `url` (string): The analyzed URL.
- `emails` (array): Extracted emails.
- `count` (int): Number of emails found.
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
