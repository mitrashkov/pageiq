# /batch-analyze/{batch_id}

**Method:** GET

**Description:**
Get status and results of a batch analysis job.

**Path Parameter:**
- `batch_id` (string, required): Batch job ID.

**Response:**
- `batch_id` (string): Batch job ID.
- `status` (string): Status (pending, processing, completed, failed).
- `progress` (float): Progress (0-1).
- `completed_count` (int): Completed URLs.
- `failed_count` (int): Failed URLs.
- `total_count` (int): Total URLs.
- `updated_at_ms` (int): Last update timestamp (ms).
- `results` (array): Results for each URL.
- `error` (string): Last error (if any).
