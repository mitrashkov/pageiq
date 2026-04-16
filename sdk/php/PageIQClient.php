<?php
/**
 * PageIQ PHP SDK
 * For use with RapidAPI
 */

class PageIQClient {
    private $apiKey;
    private $baseURL;
    private $curl;

    /**
     * Initialize the PageIQ client
     *
     * @param string $apiKey Your RapidAPI key
     * @param string $baseURL API base URL
     */
    public function __construct($apiKey, $baseURL = 'https://pageiq.p.rapidapi.com') {
        $this->apiKey = $apiKey;
        $this->baseURL = rtrim($baseURL, '/');

        $this->curl = curl_init();
        curl_setopt_array($this->curl, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_TIMEOUT => 30,
            CURLOPT_HTTPHEADER => [
                'X-RapidAPI-Key: ' . $apiKey,
                'X-RapidAPI-Host: pageiq.p.rapidapi.com',
                'Content-Type: application/json'
            ]
        ]);
    }

    /**
     * Analyze a single website
     *
     * @param string $url Website URL to analyze
     * @param array $options Analysis options
     * @return array Analysis result
     * @throws Exception On API error
     */
    public function analyzeWebsite($url, $options = []) {
        $payload = [
            'url' => $url,
            'options' => array_merge([
                'screenshot' => false,
                'use_browser' => false
            ], $options)
        ];

        return $this->makeRequest('POST', '/api/v1/analyze', $payload);
    }

    /**
     * Analyze multiple websites in batch
     *
     * @param array $urls List of URLs to analyze
     * @param array $options Batch options
     * @return array Batch analysis response
     * @throws Exception On API error
     */
    public function batchAnalyzeWebsites($urls, $options = []) {
        $payload = [
            'urls' => $urls,
            'options' => array_merge([
                'screenshot' => false
            ], $options)
        ];

        if (isset($options['webhook_url'])) {
            $payload['webhook_url'] = $options['webhook_url'];
        }

        return $this->makeRequest('POST', '/api/v1/batch-analyze', $payload);
    }

    /**
     * Get batch analysis status
     *
     * @param string $batchId Batch ID from batch analysis
     * @return array Batch status information
     * @throws Exception On API error
     */
    public function getBatchStatus($batchId) {
        return $this->makeRequest('GET', '/api/v1/batch-analyze/' . $batchId);
    }

    /**
     * Get API health status
     *
     * @return array Health status
     * @throws Exception On API error
     */
    public function getHealthStatus() {
        return $this->makeRequest('GET', '/health');
    }

    /**
     * Make HTTP request to API
     *
     * @param string $method HTTP method
     * @param string $endpoint API endpoint
     * @param array|null $data Request data
     * @return array Response data
     * @throws Exception On API error
     */
    private function makeRequest($method, $endpoint, $data = null) {
        $url = $this->baseURL . $endpoint;

        curl_setopt($this->curl, CURLOPT_URL, $url);
        curl_setopt($this->curl, CURLOPT_CUSTOMREQUEST, $method);

        if ($data !== null && in_array($method, ['POST', 'PUT', 'PATCH'])) {
            curl_setopt($this->curl, CURLOPT_POSTFIELDS, json_encode($data));
        } else {
            curl_setopt($this->curl, CURLOPT_POSTFIELDS, null);
        }

        $response = curl_exec($this->curl);
        $httpCode = curl_getinfo($this->curl, CURLINFO_HTTP_CODE);

        if (curl_error($this->curl)) {
            throw new Exception('cURL Error: ' . curl_error($this->curl));
        }

        if ($httpCode < 200 || $httpCode >= 300) {
            throw new Exception("API Error: HTTP {$httpCode} - {$response}");
        }

        return json_decode($response, true);
    }

    /**
     * Clean up cURL resource
     */
    public function __destruct() {
        if ($this->curl) {
            curl_close($this->curl);
        }
    }
}

// Example usage
function exampleUsage() {
    $client = new PageIQClient('your-rapidapi-key-here');

    try {
        // Analyze single website
        $result = $client->analyzeWebsite('https://example.com', [
            'screenshot' => true,
            'use_browser' => false
        ]);
        echo "Analysis result:\n";
        print_r($result);

        // Batch analysis
        $batchResult = $client->batchAnalyzeWebsites([
            'https://example.com',
            'https://github.com',
            'https://stackoverflow.com'
        ], [
            'webhook_url' => 'https://your-webhook-url.com/notify',
            'screenshot' => false
        ]);

        echo "\nBatch started:\n";
        print_r($batchResult);

        $batchId = $batchResult['data']['batch_id'];

        // Check status after some time
        sleep(30);
        $status = $client->getBatchStatus($batchId);
        echo "\nBatch status:\n";
        print_r($status);

    } catch (Exception $e) {
        echo "Error: " . $e->getMessage() . "\n";
    }
}

// Run example if this file is executed directly
if (basename(__FILE__) === basename($_SERVER['PHP_SELF'])) {
    exampleUsage();
}
?>