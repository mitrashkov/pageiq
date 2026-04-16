/**
 * PageIQ JavaScript SDK
 * For use with RapidAPI
 */

class PageIQClient {
    constructor(apiKey, baseURL = 'https://pageiq.p.rapidapi.com') {
        this.apiKey = apiKey;
        this.baseURL = baseURL.replace(/\/$/, '');

        this.defaultHeaders = {
            'X-RapidAPI-Key': apiKey,
            'X-RapidAPI-Host': 'pageiq.p.rapidapi.com',
            'Content-Type': 'application/json'
        };
    }

    /**
     * Analyze a single website
     * @param {string} url - Website URL to analyze
     * @param {Object} options - Analysis options
     * @param {boolean} options.screenshot - Include screenshot (Pro plan)
     * @param {boolean} options.useBrowser - Use browser automation
     * @returns {Promise<Object>} Analysis result
     */
    async analyzeWebsite(url, options = {}) {
        const payload = {
            url: url,
            options: {
                screenshot: options.screenshot || false,
                use_browser: options.useBrowser || false,
                ...options
            }
        };

        const response = await fetch(`${this.baseURL}/api/v1/analyze`, {
            method: 'POST',
            headers: this.defaultHeaders,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Analyze multiple websites in batch
     * @param {string[]} urls - Array of URLs to analyze
     * @param {Object} options - Batch options
     * @param {string} options.webhookUrl - Webhook URL for notifications
     * @param {boolean} options.screenshot - Include screenshots
     * @returns {Promise<Object>} Batch analysis response
     */
    async batchAnalyzeWebsites(urls, options = {}) {
        const payload = {
            urls: urls,
            options: {
                screenshot: options.screenshot || false,
                ...options
            }
        };

        if (options.webhookUrl) {
            payload.webhook_url = options.webhookUrl;
        }

        const response = await fetch(`${this.baseURL}/api/v1/batch-analyze`, {
            method: 'POST',
            headers: this.defaultHeaders,
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get batch analysis status
     * @param {string} batchId - Batch ID from batch analysis
     * @returns {Promise<Object>} Batch status
     */
    async getBatchStatus(batchId) {
        const response = await fetch(`${this.baseURL}/api/v1/batch-analyze/${batchId}`, {
            method: 'GET',
            headers: this.defaultHeaders
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Get health status
     * @returns {Promise<Object>} Health status
     */
    async getHealthStatus() {
        const response = await fetch(`${this.baseURL}/health`, {
            method: 'GET',
            headers: this.defaultHeaders
        });

        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }
}

// Example usage with promises
function exampleUsage() {
    const client = new PageIQClient('your-rapidapi-key-here');

    // Analyze single website
    client.analyzeWebsite('https://example.com', { screenshot: true })
        .then(result => {
            console.log('Analysis result:', result);
        })
        .catch(error => {
            console.error('Error:', error);
        });

    // Batch analysis with webhook
    client.batchAnalyzeWebsites([
        'https://example.com',
        'https://github.com',
        'https://stackoverflow.com'
    ], {
        webhookUrl: 'https://your-webhook-url.com/notify',
        screenshot: false
    })
    .then(batchResult => {
        console.log('Batch started:', batchResult);

        // Check status after some time
        setTimeout(() => {
            client.getBatchStatus(batchResult.data.batch_id)
                .then(status => console.log('Batch status:', status))
                .catch(error => console.error('Status check error:', error));
        }, 30000);
    })
    .catch(error => {
        console.error('Batch error:', error);
    });
}

// Example usage with async/await
async function asyncExample() {
    const client = new PageIQClient('your-rapidapi-key-here');

    try {
        const result = await client.analyzeWebsite('https://example.com');
        console.log('Result:', result);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Export for Node.js or browser
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PageIQClient;
} else if (typeof window !== 'undefined') {
    window.PageIQClient = PageIQClient;
}