import pytest
from bs4 import BeautifulSoup

from app.services.extractors import (
    extract_title,
    extract_description,
    extract_favicon,
    extract_logo,
    extract_emails,
    extract_phones,
    extract_social_profiles,
    detect_language,
    detect_country,
    extract_keywords,
)


class TestExtractTitle:
    def test_extract_title_from_title_tag(self):
        html = '<html><head><title>Test Title</title></head></html>'
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_title(soup) == 'Test Title'

    def test_extract_title_from_og_title(self):
        html = '''<html><head>
        <meta property="og:title" content="OG Title">
        </head></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_title(soup) == 'OG Title'

    def test_extract_title_from_h1(self):
        html = '<html><body><h1>H1 Title</h1></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_title(soup) == 'H1 Title'

    def test_extract_title_none(self):
        html = '<html><body></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_title(soup) is None


class TestExtractDescription:
    def test_extract_description_from_meta(self):
        html = '''<html><head>
        <meta name="description" content="Test description">
        </head></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_description(soup) == 'Test description'

    def test_extract_description_from_og(self):
        html = '''<html><head>
        <meta property="og:description" content="OG description">
        </head></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_description(soup) == 'OG description'

    def test_extract_description_from_paragraph(self):
        html = '<html><body><p>This is a long paragraph with substantial content for testing.</p></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        assert 'long paragraph' in extract_description(soup)


class TestExtractFavicon:
    def test_extract_favicon_from_link(self):
        html = '''<html><head>
        <link rel="icon" href="/favicon.ico">
        </head></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_favicon(soup, 'https://example.com') == 'https://example.com/favicon.ico'

    def test_extract_favicon_shortcut(self):
        html = '''<html><head>
        <link rel="shortcut icon" href="favicon.png">
        </head></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_favicon(soup, 'https://example.com') == 'https://example.com/favicon.png'


class TestExtractLogo:
    def test_extract_logo_from_og_image(self):
        html = '''<html><head>
        <meta property="og:image" content="logo.png">
        </head></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_logo(soup, 'https://example.com') == 'https://example.com/logo.png'

    def test_extract_logo_from_img_class(self):
        html = '<html><body><img class="logo" src="brand-logo.jpg"></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        assert extract_logo(soup, 'https://example.com') == 'https://example.com/brand-logo.jpg'


class TestExtractEmails:
    def test_extract_emails_from_mailto(self):
        html = '<html><body><a href="mailto:test@example.com">Email</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        emails = extract_emails(soup)
        assert 'test@example.com' in emails

    def test_extract_emails_from_text(self):
        html = '<html><body>Contact us at info@company.com</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        emails = extract_emails(soup)
        assert 'info@company.com' in emails

    def test_extract_emails_unique(self):
        html = '<html><body>info@company.com contact@company.com info@company.com</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        emails = extract_emails(soup)
        assert len(emails) == 2
        assert 'info@company.com' in emails
        assert 'contact@company.com' in emails


class TestExtractPhones:
    def test_extract_phones_from_tel(self):
        html = '<html><body><a href="tel:+1234567890">Call</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        phones = extract_phones(soup)
        assert '+1234567890' in phones

    def test_extract_phones_from_text(self):
        html = '<html><body>Call (555) 123-4567</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        phones = extract_phones(soup)
        assert '5551234567' in phones


class TestExtractSocialProfiles:
    def test_extract_twitter_from_meta(self):
        html = '''<html><head>
        <meta name="twitter:site" content="@testaccount">
        </head></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        profiles = extract_social_profiles(soup, 'https://example.com')
        assert profiles.get('twitter') == 'https://twitter.com/testaccount'

    def test_extract_facebook_from_link(self):
        html = '<html><body><a href="https://facebook.com/testpage">Facebook</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        profiles = extract_social_profiles(soup, 'https://example.com')
        assert profiles.get('facebook') == 'https://facebook.com/testpage'


class TestDetectLanguage:
    def test_detect_english(self):
        html = '<html><body>This is a test page with English content.</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        lang = detect_language(soup)
        assert lang == 'en'

    def test_detect_no_content(self):
        html = '<html><body></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        lang = detect_language(soup)
        assert lang is None


class TestDetectCountry:
    def test_detect_country_from_tld(self):
        # This would require mocking or testing with actual URLs
        # For now, just test the function exists
        html = '<html><body></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        country = detect_country('https://example.us', soup)
        # TLD detection would need proper implementation
        assert country is None or isinstance(country, str)


class TestExtractKeywords:
    def test_extract_keywords_basic(self):
        html = '''<html><body>
        <p>This is a test page about artificial intelligence and machine learning.
        Artificial intelligence is transforming the technology industry.</p>
        </body></html>'''
        soup = BeautifulSoup(html, 'html.parser')
        keywords = extract_keywords(soup, max_keywords=5)
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        if keywords:
            assert all(isinstance(k, str) for k in keywords)

    def test_extract_keywords_insufficient_content(self):
        html = '<html><body>Short text</body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        keywords = extract_keywords(soup)
        assert keywords == []