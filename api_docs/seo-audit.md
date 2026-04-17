# /seo/seo-audit

**Method:** POST

**Description:**
Perform a comprehensive SEO audit on a webpage. Checks title, meta description, headings, images, structured data, Open Graph, mobile friendliness, robots.txt, and more.

**Request Body:**
- `url` (string, required): Website URL to audit.
- `options` (object, optional): Audit options.

**Response:**
- `url` (string): The analyzed URL.
- `score` (int): SEO score (0-100).
- `audit_items` (array): List of audit checks and results.
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
