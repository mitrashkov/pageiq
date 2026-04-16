import pytest

from app.utils.url import (
    validate_url,
    normalize_url,
    extract_domain,
    get_base_url,
    resolve_url,
    extract_tld,
    is_valid_domain,
)


class TestValidateUrl:
    def test_valid_http_url(self):
        assert validate_url('http://example.com') is True

    def test_valid_https_url(self):
        assert validate_url('https://example.com') is True

    def test_invalid_url(self):
        assert validate_url('not-a-url') is False

    def test_none_url(self):
        assert validate_url(None) is False

    def test_empty_url(self):
        assert validate_url('') is False


class TestNormalizeUrl:
    def test_normalize_with_fragment(self):
        url = 'https://example.com/page?param=value#section'
        normalized = normalize_url(url)
        assert normalized == 'https://example.com/page'

    def test_normalize_with_query(self):
        url = 'https://example.com/page?param=value'
        normalized = normalize_url(url)
        assert normalized == 'https://example.com/page'

    def test_normalize_trailing_slash(self):
        url = 'https://example.com/page/'
        normalized = normalize_url(url)
        assert normalized == 'https://example.com/page'

    def test_normalize_invalid_url(self):
        with pytest.raises(ValueError):
            normalize_url('not-a-url')


class TestExtractDomain:
    def test_extract_domain_basic(self):
        domain = extract_domain('https://sub.example.com/page')
        assert domain == 'example.com'

    def test_extract_domain_tld(self):
        domain = extract_domain('https://example.co.uk/page')
        assert domain == 'example.co.uk'

    def test_extract_domain_invalid(self):
        with pytest.raises(ValueError):
            extract_domain('not-a-url')


class TestGetBaseUrl:
    def test_get_base_url(self):
        base = get_base_url('https://example.com/page')
        assert base == 'https://example.com'

    def test_get_base_url_with_port(self):
        base = get_base_url('https://example.com:8080/page')
        assert base == 'https://example.com:8080'


class TestResolveUrl:
    def test_resolve_absolute_url(self):
        resolved = resolve_url('https://example.com', 'https://other.com/page')
        assert resolved == 'https://other.com/page'

    def test_resolve_relative_url(self):
        resolved = resolve_url('https://example.com', '/page')
        assert resolved == 'https://example.com/page'

    def test_resolve_relative_path(self):
        resolved = resolve_url('https://example.com/dir/', 'page.html')
        assert resolved == 'https://example.com/dir/page.html'


class TestExtractTld:
    def test_extract_tld_com(self):
        tld = extract_tld('https://example.com')
        assert tld == 'com'

    def test_extract_tld_co_uk(self):
        tld = extract_tld('https://example.co.uk')
        assert tld == 'co.uk'

    def test_extract_tld_invalid(self):
        tld = extract_tld('not-a-url')
        assert tld is None


class TestIsValidDomain:
    def test_valid_domain(self):
        assert is_valid_domain('example.com') is True

    def test_valid_domain_with_subdomain(self):
        assert is_valid_domain('sub.example.com') is True

    def test_invalid_domain(self):
        assert is_valid_domain('not-a-domain') is False

    def test_empty_domain(self):
        assert is_valid_domain('') is False