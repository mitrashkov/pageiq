# /extract/schema

**Method:** POST

**Description:**
Extract Schema.org structured data and Open Graph tags from a webpage.

**Request Body:**
- `url` (string, required): Website URL to extract schema from.
- `options` (object, optional): Extraction options.

**Response:**
- `url` (string): The analyzed URL.
- `schema_org` (object|null): Extracted Schema.org data (null if not found).
- `og_tags` (object|null): Extracted Open Graph tags (null if not found).
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
