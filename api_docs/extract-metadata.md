# /extract/metadata

**Method:** POST

**Description:**
Extract consolidated metadata from a webpage in one call.

**Request Body:**
- `url` (string, required): Website URL to extract metadata from.
- `options` (object, optional): Extraction options.
- `options.use_browser` (bool): Enables browser rendering for JS-heavy pages.

**Response:**
- `url` (string): The analyzed URL.
- `title` (string|null): Page title.
- `description` (string|null): Page description.
- `schema_org` (object|null): Extracted Schema.org data.
- `og_tags` (object|null): Extracted Open Graph tags.
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
