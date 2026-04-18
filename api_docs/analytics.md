# /analytics

**Methods:** GET

**Description:**
Usage and performance analytics endpoints.

**Endpoints:**
- `/analytics/` (GET): Returns aggregate usage stats, popular domains, and performance summary.
- `/analytics/performance` (GET): Returns detailed performance metrics.
- `/analytics/endpoints` (GET): Returns usage breakdown by endpoint.

**Query Parameters:**
- `days` (int, optional): Lookback window in days. Range: `1` to `90`. Default: `7`.

**Response Envelope:**
- Returns standard API success envelope with `success`, `data`, `message`, `request_id`, and metadata fields.
