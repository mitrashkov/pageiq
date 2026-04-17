# /seo/broken-links

**Method:** POST

**Description:**
Detect broken links on a webpage. Scans all links and checks if they are valid.

**Request Body:**
- `url` (string, required): Website URL to check.
- `check_external` (boolean, optional): Whether to check external links.
- `options` (object, optional): Extraction options.

**Response:**
- `url` (string): The analyzed URL.
- `total_links` (int): Total links found.
- `broken_links_count` (int): Number of broken links.
- `internal_links` (int): Number of internal links.
- `external_links` (int): Number of external links.
- `broken_links` (array): List of broken links and errors.
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
