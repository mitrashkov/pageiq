# /extract/emails

**Method:** POST

**Description:**
Extract email addresses from a webpage or an entire website. Returns validated, unique email addresses.

**Request Body:**
- `url` (string, required): Website URL to extract emails from.
- `options` (object, optional): Extraction options.
    - `deep_search` (bool): If true, crawls the website to find emails on multiple pages (default: false). **Available on Pro, Business, and Enterprise plans.**
    - `pages_limit` (int): Maximum number of pages to crawl during deep search (default: 10, max: 20).

**Response:**
- `url` (string): The analyzed URL.
- `emails` (array): Extracted emails.
- `count` (int): Number of emails found.
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
