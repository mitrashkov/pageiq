# /analyze/tech

**Method:** POST

**Description:**
Detect web technologies and foundational web languages used by a website.

**Request Body:**
- `url` (string, required): Website URL to inspect.
- `options` (object, optional): Detection options.
- `options.use_browser` (bool): Enables browser rendering for JS-heavy pages before detection.

**Response:**
- `url` (string): The analyzed URL.
- `languages` (array[string]): Detected web languages, such as `HTML`, `CSS`, `JavaScript`.
- `technologies` (array[string]): Full detected stack (frameworks, platforms, analytics, and languages).
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
