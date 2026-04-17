# /analytics

**Method:** GET

**Description:**
Get usage analytics for the API, including usage stats, popular domains, and performance metrics.

**Query Parameters:**
- `days` (int, optional): Number of days to look back (default: 7).

**Response:**
- `usage_stats` (object): Usage statistics.
- `popular_domains` (array): Popular domains.
- `performance_metrics` (object): Performance metrics.
- `generated_at` (string): Timestamp.

# /analytics/performance

**Method:** GET

**Description:**
Get detailed performance metrics (response times, error rates, uptime, etc.).

**Query Parameters:**
- `days` (int, optional): Number of days to look back (default: 7).

**Response:**
- `data` (object): Performance metrics.
- `message` (string): Info message.

# /analytics/endpoints

**Method:** GET

**Description:**
Get usage statistics by endpoint (popularity, performance).

**Query Parameters:**
- `days` (int, optional): Number of days to look back (default: 7).

**Response:**
- `total_endpoints` (int): Number of endpoints.
- `endpoint_usage` (object): Usage by endpoint.
- `top_endpoints` (array): Most popular endpoints.
- `message` (string): Info message.
