# /extract/metadata

**Method:** POST

**Description:**
Extract all metadata from a webpage, including title, description, schema.org, and Open Graph tags.

**Request Body:**
- `url` (string, required): Website URL to extract metadata from.
- `options` (object, optional): Extraction options.

**Response:**
- `url` (string): The analyzed URL.
- `title` (string): Page title.
- `description` (string): Page description.
- `schema_org` (object): Schema.org data.
- `og_tags` (object): Open Graph tags.
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
