"""
Unit tests for Instagram scraper service
"""
import pytest
from unittest.mock import AsyncMock

from src.services.instagram_scraper import (
    InstagramAuthRequired,
    InstagramScraper,
    InstagramScraperError,
)


class TestInstagramScraper:
    """Test suite for InstagramScraper"""

    @pytest.fixture
    def scraper(self) -> InstagramScraper:
        """Create InstagramScraper instance"""
        return InstagramScraper(headless=True)

    def test_scraper_initialization(self, scraper: InstagramScraper) -> None:
        """Test that scraper initializes with default dependencies"""
        assert scraper.rate_limiter is not None
        assert scraper.retry_handler is not None
        assert scraper.headless is True

    def test_scraper_custom_dependencies(self) -> None:
        """Test scraper with custom dependencies"""
        from src.services.rate_limiter import RateLimiter
        from src.services.retry_handler import RetryHandler

        rate_limiter = RateLimiter(min_delay=1.0, max_delay=2.0)
        retry_handler = RetryHandler(max_retries=5)

        scraper = InstagramScraper(
            rate_limiter=rate_limiter,
            retry_handler=retry_handler,
            headless=False,
        )

        assert scraper.rate_limiter is rate_limiter
        assert scraper.retry_handler is retry_handler
        assert scraper.headless is False

    @pytest.mark.asyncio
    async def test_check_auth_required_url(self, scraper: InstagramScraper) -> None:
        """Test auth detection from URL"""
        mock_page = AsyncMock()

        # Test login URL
        mock_page.url = "https://www.instagram.com/accounts/login/"
        assert await scraper._check_auth_required(mock_page) is True

        # Test normal URL
        mock_page.url = "https://www.instagram.com/p/ABC123/"
        mock_page.locator.return_value.first.is_visible = AsyncMock(return_value=False)
        assert await scraper._check_auth_required(mock_page) is False

    @pytest.mark.asyncio
    async def test_extract_post_data(self, scraper: InstagramScraper) -> None:
        """Test post data extraction"""
        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.first.inner_text = AsyncMock(return_value="Test caption")
        mock_page.locator.return_value = mock_locator

        post_url = "https://www.instagram.com/p/ABC123/"
        post_data = await scraper._extract_post_data(mock_page, post_url)

        assert post_data["platform"] == "instagram"
        assert post_data["post_url"] == post_url
        assert "post_time" in post_data
        assert post_data["likes_count"] >= 0
        assert post_data["comments_count"] >= 0

    def test_instagram_auth_required_exception(self) -> None:
        """Test InstagramAuthRequired exception"""
        exc = InstagramAuthRequired("Login required")
        assert str(exc) == "Login required"
        assert isinstance(exc, InstagramScraperError)

    def test_instagram_scraper_error_exception(self) -> None:
        """Test InstagramScraperError base exception"""
        exc = InstagramScraperError("Scraping failed")
        assert str(exc) == "Scraping failed"
        assert isinstance(exc, Exception)
