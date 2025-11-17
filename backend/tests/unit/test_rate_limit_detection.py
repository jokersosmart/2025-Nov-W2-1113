"""
Unit tests for rate limit detection logic

Tests detection of rate limiting signals from social media platforms.
"""
import pytest
from playwright.async_api import Page, Response

from src.api.middleware.error_handler import RateLimitError


@pytest.fixture
def mock_response():
    """Create mock response object"""

    class MockResponse:
        def __init__(self, status=200, headers=None):
            self.status = status
            self.headers = headers or {}

        async def text(self):
            return ""

    return MockResponse


# RED: Write failing tests first
class TestRateLimitDetection:
    """Test rate limit detection from HTTP responses"""

    def test_detect_http_429_status(self, mock_response):
        """HTTP 429 status code should be detected as rate limit"""
        from src.services.rate_limit_detector import detect_rate_limit

        response = mock_response(status=429)
        is_limited, retry_after = detect_rate_limit(response)

        assert is_limited is True
        assert retry_after >= 60  # Default retry after

    def test_detect_retry_after_header(self, mock_response):
        """Retry-After header should be parsed correctly"""
        from src.services.rate_limit_detector import detect_rate_limit

        response = mock_response(status=429, headers={"Retry-After": "120"})
        is_limited, retry_after = detect_rate_limit(response)

        assert is_limited is True
        assert retry_after == 120

    def test_detect_x_rate_limit_headers(self, mock_response):
        """X-RateLimit headers should indicate rate limiting"""
        from src.services.rate_limit_detector import detect_rate_limit

        response = mock_response(
            status=200,
            headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1234567890"},
        )
        is_limited, retry_after = detect_rate_limit(response)

        assert is_limited is True

    def test_no_rate_limit_on_normal_response(self, mock_response):
        """Normal responses should not be detected as rate limited"""
        from src.services.rate_limit_detector import detect_rate_limit

        response = mock_response(status=200)
        is_limited, retry_after = detect_rate_limit(response)

        assert is_limited is False
        assert retry_after == 0


class TestPageContentDetection:
    """Test rate limit detection from page content"""

    @pytest.mark.asyncio
    async def test_detect_facebook_checkpoint(self):
        """Facebook checkpoint page should be detected"""
        from src.services.rate_limit_detector import detect_rate_limit_from_page

        class MockPage:
            @property
            def url(self):
                return "https://www.facebook.com/checkpoint/"

            async def content(self):
                return "<html><body>Checkpoint</body></html>"

        page = MockPage()
        is_limited = await detect_rate_limit_from_page(page)

        assert is_limited is True

    @pytest.mark.asyncio
    async def test_detect_instagram_challenge(self):
        """Instagram challenge page should be detected"""
        from src.services.rate_limit_detector import detect_rate_limit_from_page

        class MockPage:
            @property
            def url(self):
                return "https://www.instagram.com/challenge/"

            async def content(self):
                return "<html><body>Challenge Required</body></html>"

        page = MockPage()
        is_limited = await detect_rate_limit_from_page(page)

        assert is_limited is True

    @pytest.mark.asyncio
    async def test_detect_rate_limit_keywords_in_content(self):
        """Rate limit keywords in page content should be detected"""
        from src.services.rate_limit_detector import detect_rate_limit_from_page

        class MockPage:
            @property
            def url(self):
                return "https://www.facebook.com/test"

            async def content(self):
                return "<html><body>Too many requests. Please try again later.</body></html>"

        page = MockPage()
        is_limited = await detect_rate_limit_from_page(page)

        assert is_limited is True

    @pytest.mark.asyncio
    async def test_detect_captcha_presence(self):
        """CAPTCHA presence should indicate rate limiting"""
        from src.services.rate_limit_detector import detect_rate_limit_from_page

        class MockPage:
            @property
            def url(self):
                return "https://www.facebook.com/test"

            async def content(self):
                return '<html><body><div class="g-recaptcha">CAPTCHA</div></body></html>'

        page = MockPage()
        is_limited = await detect_rate_limit_from_page(page)

        assert is_limited is True

    @pytest.mark.asyncio
    async def test_no_rate_limit_on_normal_page(self):
        """Normal page content should not be detected as rate limited"""
        from src.services.rate_limit_detector import detect_rate_limit_from_page

        class MockPage:
            @property
            def url(self):
                return "https://www.facebook.com/test/posts/123"

            async def content(self):
                return "<html><body><div>Normal post content</div></body></html>"

        page = MockPage()
        is_limited = await detect_rate_limit_from_page(page)

        assert is_limited is False


class TestRateLimitErrorRaising:
    """Test raising RateLimitError when detection occurs"""

    def test_check_rate_limit_raises_error_on_429(self, mock_response):
        """check_rate_limit should raise RateLimitError on 429"""
        from src.services.rate_limit_detector import check_rate_limit

        response = mock_response(status=429, headers={"Retry-After": "90"})

        with pytest.raises(RateLimitError) as exc_info:
            check_rate_limit(response)

        assert "平台偵測到頻繁存取" in str(exc_info.value)
        assert exc_info.value.retry_after == 90

    def test_check_rate_limit_passes_on_normal_response(self, mock_response):
        """check_rate_limit should not raise on normal response"""
        from src.services.rate_limit_detector import check_rate_limit

        response = mock_response(status=200)

        # Should not raise
        check_rate_limit(response)

    @pytest.mark.asyncio
    async def test_check_page_rate_limit_raises_on_checkpoint(self):
        """check_page_rate_limit should raise on checkpoint page"""
        from src.services.rate_limit_detector import check_page_rate_limit

        class MockPage:
            @property
            def url(self):
                return "https://www.facebook.com/checkpoint/"

            async def content(self):
                return "<html><body>Checkpoint</body></html>"

        page = MockPage()

        with pytest.raises(RateLimitError) as exc_info:
            await check_page_rate_limit(page)

        assert "平台偵測到頻繁存取" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_check_page_rate_limit_passes_on_normal_page(self):
        """check_page_rate_limit should not raise on normal page"""
        from src.services.rate_limit_detector import check_page_rate_limit

        class MockPage:
            @property
            def url(self):
                return "https://www.facebook.com/test/posts/123"

            async def content(self):
                return "<html><body>Normal content</body></html>"

        page = MockPage()

        # Should not raise
        await check_page_rate_limit(page)


class TestIntegrationWithScrapers:
    """Test integration with scraper classes"""

    def test_scraper_can_import_detection_functions(self):
        """Scrapers should be able to import detection functions"""
        # This test ensures the module is properly structured
        from src.services.rate_limit_detector import (
            check_page_rate_limit,
            check_rate_limit,
            detect_rate_limit,
            detect_rate_limit_from_page,
        )

        # All functions should be callable
        assert callable(detect_rate_limit)
        assert callable(detect_rate_limit_from_page)
        assert callable(check_rate_limit)
        assert callable(check_page_rate_limit)
