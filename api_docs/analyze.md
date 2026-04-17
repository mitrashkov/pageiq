# /analyze

**Method:** POST

**Description:**
Analyze a website and return structured business data including metadata, contacts, tech stack, schema, Open Graph, keywords, screenshot, and more.

**Request Body:**
- `url` (string, required): Website URL to analyze.
- `options` (object, optional): Additional options (e.g., `wait_for_js`, `screenshot`).

**Response:**
- `url` (string): The analyzed URL.
- `title` (string): Page title.
- `description` (string): Page description.
- `logo` (string): Logo URL.
- `favicon` (string): Favicon URL.
- `emails` (array): Extracted emails.
- `phones` (array): Extracted phone numbers.
- `socials` (array): Social profiles.
- `tech_stack` (array): Detected technologies.
- `industry_guess` (object): Industry label and confidence.
- `language` (string): Detected language.
- `country_guess` (string): Detected country.
- `keywords` (array): Extracted keywords.
- `schema_org` (object): Schema.org data.
- `og_tags` (object): Open Graph tags.
- `screenshot_url` (string): Screenshot URL (if requested).
- `page_speed_score` (int): Page speed score.
- `ai_summary` (string): AI-generated summary.
- `timestamp` (int): Timestamp (ms).
- `processing_time_ms` (int): Processing time (ms).
- `diagnostics` (object): Diagnostics and fallback info.
