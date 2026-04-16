import pytest
from unittest.mock import Mock, patch

from app.services.fetcher import HTMLFetcher


class TestHTMLFetcher:
    def test_fetch_html_success(self):
        fetcher = HTMLFetcher()

        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = '<html><body>Test</body></html>'
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            html, error, headers = fetcher.fetch_html('https://example.com')

            assert html == '<html><body>Test</body></html>'
            assert error is None
            assert headers == {'content-type': 'text/html'}

    def test_fetch_html_non_html_content(self):
        fetcher = HTMLFetcher()

        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.text = 'Not HTML'
            mock_response.headers = {'content-type': 'application/json'}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            html, error, headers = fetcher.fetch_html('https://api.example.com')

            assert html is None
            assert 'Content type' in error
            assert headers == {'content-type': 'application/json'}

    def test_fetch_html_request_error(self):
        fetcher = HTMLFetcher()

        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = Exception('Connection error')

            html, error, headers = fetcher.fetch_html('https://example.com')

            assert html is None
            assert 'Connection error' in error
            assert headers == {}

    def test_parse_html_success(self):
        fetcher = HTMLFetcher()
        html = '<html><body><h1>Title</h1></body></html>'

        soup = fetcher.parse_html(html)

        assert soup is not None
        assert soup.find('h1').text == 'Title'

    def test_parse_html_invalid(self):
        fetcher = HTMLFetcher()
        html = 'Invalid HTML <'

        soup = fetcher.parse_html(html)

        assert soup is None