# /extract/emails

**Method:** POST

**Description:**
Extract email addresses from a webpage. Returns validated, unique email addresses.

**Request Body:**
- `url` (string, required): Website URL to extract emails from.
- `options` (object, optional): Extraction options.

**Response:**
- `url` (string): The analyzed URL.
- `emails` (array): Extracted emails.
- `count` (int): Number of emails found.
- `timestamp` (float): Timestamp.
- `processing_time_ms` (int): Processing time (ms).
