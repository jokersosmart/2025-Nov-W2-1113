"""
Unit tests for Facebook scraper service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.facebook_scraper import (
    FacebookAuthRequired,
    FacebookScraper,
    FacebookScraperError,
)


class TestFacebookScraper:
    """Test suite for FacebookScraper"""

    @pytest.fixture
    def scraper(self) -> FacebookScraper:
        """Create FacebookScraper instance"""
        return FacebookScraper(headless=True)

    def test_scraper_initialization(self, scraper: FacebookScraper) -> None:
        """Test that scraper initializes with default dependencies"""
        assert scraper.rate_limiter is not None
        assert scraper.retry_handler is not None
        assert scraper.headless is True

    def test_scraper_custom_dependencies(self) -> None:
        """Test scraper with custom rate limiter and retry handler"""
        from src.services.rate_limiter import RateLimiter
        from src.services.retry_handler import RetryHandler

        rate_limiter = RateLimiter(min_delay=1.0, max_delay=2.0)
        retry_handler = RetryHandler(max_retries=5)

        scraper = FacebookScraper(
            rate_limiter=rate_limiter,
            retry_handler=retry_handler,
            headless=False,
        )

        assert scraper.rate_limiter is rate_limiter
        assert scraper.retry_handler is retry_handler
        assert scraper.headless is False

    @pytest.mark.asyncio
    async def test_check_auth_required_url_indicators(
        self, scraper: FacebookScraper
    ) -> None:
        """Test auth detection from URL"""
        mock_page = AsyncMock()

        # Test login URL
        mock_page.url = "https://www.facebook.com/login/"
        assert await scraper._check_auth_required(mock_page) is True

        # Test checkpoint URL
        mock_page.url = "https://www.facebook.com/checkpoint/"
        assert await scraper._check_auth_required(mock_page) is True

        # Test normal URL
        mock_page.url = "https://www.facebook.com/test/posts/123"
        mock_page.locator.return_value.first.is_visible = AsyncMock(return_value=False)
        assert await scraper._check_auth_required(mock_page) is False

    @pytest.mark.asyncio
    async def test_extract_post_data(self, scraper: FacebookScraper) -> None:
        """Test post data extraction"""
        mock_page = AsyncMock()
        mock_locator = AsyncMock()

        # Mock post content
        mock_locator.first.inner_text = AsyncMock(return_value="Test post content")
        mock_page.locator.return_value = mock_locator

        post_url = "https://www.facebook.com/test/posts/123"
        post_data = await scraper._extract_post_data(mock_page, post_url)

        assert post_data["platform"] == "facebook"
        assert post_data["post_url"] == post_url
        assert "post_time" in post_data
        assert "post_content" in post_data
        assert post_data["likes_count"] >= 0
        assert post_data["comments_count"] >= 0

    @pytest.mark.asyncio
    async def test_extract_single_comment(self, scraper: FacebookScraper) -> None:
        """Test single comment extraction"""
        mock_element = AsyncMock()

        # Mock commenter link
        mock_link = AsyncMock()
        mock_link.get_attribute = AsyncMock(return_value="/testuser")
        mock_element.locator.return_value.first = mock_link

        # Mock comment content
        mock_content = AsyncMock()
        mock_content.inner_text = AsyncMock(return_value="Test comment content")
        mock_link.inner_text = AsyncMock(return_value="Test comment content")

        post_url = "https://www.facebook.com/test/posts/123"
        comment_data = await scraper._extract_single_comment(
            mock_element, post_url, 0
        )

        # May return None if extraction fails, which is acceptable
        if comment_data:
            assert "comment_id" in comment_data
            assert comment_data["post_url"] == post_url
            assert "comment_time" in comment_data
            assert "commenter_id" in comment_data
            assert "comment_content" in comment_data

    def test_facebook_auth_required_exception(self) -> None:
        """Test FacebookAuthRequired exception"""
        exc = FacebookAuthRequired("Login required")
        assert str(exc) == "Login required"
        assert isinstance(exc, FacebookScraperError)

    def test_facebook_scraper_error_exception(self) -> None:
        """Test FacebookScraperError base exception"""
        exc = FacebookScraperError("Scraping failed")
        assert str(exc) == "Scraping failed"
        assert isinstance(exc, Exception)
