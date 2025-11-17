"""
Unit tests for rate limit detector

Tests the rate limit detection logic following TDD principles.
"""
import pytest

from src.api.middleware.error_handler import RateLimitError
from src.services.rate_limit_detector import (
    check_page_rate_limit,
    check_rate_limit,
    check_response_and_page,
    detect_rate_limit,
    detect_rate_limit_from_page,
)


class TestHTTPStatusDetection:
    """Test HTTP status code based detection"""

    def test_detect_429_status_code(self):
        """Should detect HTTP 429 Too Many Requests"""

        class MockResponse:
            status = 429
            headers = {"retry-after": "120"}

        is_limited, retry_after = detect_rate_limit(MockResponse())

        assert is_limited is True
        assert retry_after == 120

    def test_detect_429_without_retry_after(self):
        """Should detect 429 even without Retry-After header"""

        class MockResponse:
            status = 429
            headers = {}

        is_limited, retry_after = detect_rate_limit(MockResponse())

        assert is_limited is True
        assert retry_after == 60  # Default

    def test_normal_status_not_detected(self):
        """Should not detect rate limit for normal status codes"""

        class MockResponse:
            status = 200
            headers = {}

        is_limited, retry_after = detect_rate_limit(MockResponse())

        assert is_limited is False
        assert retry_after == 0

    def test_x_ratelimit_remaining_zero(self):
        """Should detect when X-RateLimit-Remaining is 0"""

        class MockResponse:
            status = 200
            headers = {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "1700000000"}

        is_limited, retry_after = detect_rate_limit(MockResponse())

        assert is_limited is True
        assert retry_after > 0


class TestContentBasedDetection:
    """Test content-based rate limit detection"""

    @pytest.mark.asyncio
    async def test_detect_checkpoint_url(self):
        """Should detect Facebook checkpoint URL"""

        class MockPage:
            url = "https://www.facebook.com/checkpoint/?next=https://..."

            async def content(self):
                return "<html><body>Checkpoint</body></html>"

        is_limited = await detect_rate_limit_from_page(MockPage())
        assert is_limited is True

    @pytest.mark.asyncio
    async def test_detect_challenge_url(self):
        """Should detect Instagram challenge URL"""

        class MockPage:
            url = "https://www.instagram.com/challenge/..."

            async def content(self):
                return "<html><body>Challenge</body></html>"

        is_limited = await detect_rate_limit_from_page(MockPage())
        assert is_limited is True

    @pytest.mark.asyncio
    async def test_detect_rate_limit_keywords(self):
        """Should detect rate limit related keywords"""

        class MockPage:
            url = "https://www.facebook.com/post/123"

            async def content(self):
                return "<html><body><h1>Too Many Requests</h1></body></html>"

        is_limited = await detect_rate_limit_from_page(MockPage())
        assert is_limited is True

    @pytest.mark.asyncio
    async def test_detect_chinese_keywords(self):
        """Should detect Chinese rate limit messages"""

        class MockPage:
            url = "https://www.facebook.com/post/123"

            async def content(self):
                return "<html><body><p>頻繁存取</p></body></html>"

        is_limited = await detect_rate_limit_from_page(MockPage())
        assert is_limited is True

    @pytest.mark.asyncio
    async def test_detect_captcha(self):
        """Should detect CAPTCHA requirement"""

        class MockPage:
            url = "https://www.facebook.com/post/123"

            async def content(self):
                return '<html><body><div class="g-recaptcha"></div></body></html>'

        is_limited = await detect_rate_limit_from_page(MockPage())
        assert is_limited is True

    @pytest.mark.asyncio
    async def test_normal_content_not_detected(self):
        """Should not detect rate limit in normal content"""

        class MockPage:
            url = "https://www.facebook.com/post/123"

            async def content(self):
                return "<html><body><div class='post'>Normal post</div></body></html>"

        is_limited = await detect_rate_limit_from_page(MockPage())
        assert is_limited is False


class TestCheckFunctions:
    """Test convenience check functions that raise errors"""

    def test_check_rate_limit_raises_on_429(self):
        """check_rate_limit should raise RateLimitError for 429"""

        class MockResponse:
            status = 429
            headers = {"retry-after": "90"}

        with pytest.raises(RateLimitError) as exc_info:
            check_rate_limit(MockResponse())

        assert exc_info.value.retry_after == 90

    def test_check_rate_limit_passes_on_200(self):
        """check_rate_limit should not raise for normal responses"""

        class MockResponse:
            status = 200
            headers = {}

        # Should not raise
        check_rate_limit(MockResponse())

    @pytest.mark.asyncio
    async def test_check_page_rate_limit_raises(self):
        """check_page_rate_limit should raise RateLimitError when detected"""

        class MockPage:
            url = "https://www.facebook.com/checkpoint/"

            async def content(self):
                return "<html><body>Checkpoint</body></html>"

        with pytest.raises(RateLimitError):
            await check_page_rate_limit(MockPage())

    @pytest.mark.asyncio
    async def test_check_page_rate_limit_passes(self):
        """check_page_rate_limit should not raise for normal pages"""

        class MockPage:
            url = "https://www.facebook.com/post/123"

            async def content(self):
                return "<html><body>Normal content</body></html>"

        # Should not raise
        await check_page_rate_limit(MockPage())

    @pytest.mark.asyncio
    async def test_check_response_and_page_combines_checks(self):
        """check_response_and_page should check both response and page"""

        class MockResponse:
            status = 429
            headers = {}

        class MockPage:
            url = "https://www.facebook.com/post/123"

            async def content(self):
                return "<html><body>Normal</body></html>"

        # Should raise due to 429 status
        with pytest.raises(RateLimitError):
            await check_response_and_page(MockResponse(), MockPage())


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_missing_status_attribute(self):
        """Should handle response without status attribute"""

        class MockResponse:
            headers = {}

        is_limited, retry_after = detect_rate_limit(MockResponse())
        assert is_limited is False

    def test_missing_headers_attribute(self):
        """Should handle response without headers attribute"""

        class MockResponse:
            status = 200

        is_limited, retry_after = detect_rate_limit(MockResponse())
        assert is_limited is False

    @pytest.mark.asyncio
    async def test_page_content_exception_not_detected(self):
        """Should return False if page.content() raises"""

        class MockPage:
            url = "https://www.facebook.com/post/123"

            async def content(self):
                raise Exception("Cannot read content")

        # Should not raise, should return False
        is_limited = await detect_rate_limit_from_page(MockPage())
        assert is_limited is False

    def test_retry_after_non_numeric(self):
        """Should handle non-numeric Retry-After header"""

        class MockResponse:
            status = 429
            headers = {"retry-after": "Wed, 21 Oct 2025 07:28:00 GMT"}

        is_limited, retry_after = detect_rate_limit(MockResponse())

        assert is_limited is True
        assert retry_after == 60  # Default when parsing fails

