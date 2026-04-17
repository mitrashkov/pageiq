# /batch-analyze

**Method:** POST

**Description:**
Analyze multiple websites in batch. Processes up to 100 URLs per request. Results are available via batch status endpoint and optional webhook.

**Request Body:**
- `urls` (array, required): List of URLs to analyze.
- `options` (object, optional): Options for analysis.
- `webhook_url` (string, optional): Webhook for completion notification.

**Response:**
- `batch_id` (string): Unique batch job ID.
- `urls_count` (int): Number of URLs in batch.
- `estimated_completion_time` (int): Estimated time (seconds).
- `webhook_url` (string): Webhook URL (if provided).
