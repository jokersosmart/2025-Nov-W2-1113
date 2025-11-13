"""
Unit tests for URL validator utility
"""
import pytest

from src.utils.url_validator import (
    URLValidator,
    ValidationResult,
    ValidationStatus,
    validate_url,
)


class TestURLValidator:
    """Test suite for URLValidator"""

    # Facebook valid URLs
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.facebook.com/username/posts/123456789",
            "https://m.facebook.com/username/posts/987654321",
            "https://facebook.com/page.name/posts/111222333",
            "http://www.facebook.com/user123/posts/999888777",
            "https://www.facebook.com/photo?fbid=123456",
            "https://www.facebook.com/photo.php?fbid=789012",
            "https://m.facebook.com/photo.php?fbid=345678",
            "https://www.facebook.com/story.php?story_fbid=123&id=456",
            "https://facebook.com/permalink.php?story_fbid=789&id=012",
        ],
    )
    def test_valid_facebook_urls(self, url: str) -> None:
        """Test that valid Facebook URLs are accepted"""
        result = validate_url(url)
        assert result.is_valid
        assert result.status == ValidationStatus.VALID
        assert result.platform == "facebook"

    # Instagram valid URLs
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.instagram.com/p/ABC123xyz/",
            "https://instagram.com/p/XYZ789abc",
            "http://www.instagram.com/p/test_post-123",
            "https://www.instagram.com/reel/DEF456uvw/",
            "https://instagram.com/reel/GHI789rst",
        ],
    )
    def test_valid_instagram_urls(self, url: str) -> None:
        """Test that valid Instagram URLs are accepted"""
        result = validate_url(url)
        assert result.is_valid
        assert result.status == ValidationStatus.VALID
        assert result.platform == "instagram"

    # Invalid Facebook URLs
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.facebook.com/username",  # No /posts/
            "https://www.facebook.com/",  # Root URL
            "https://www.facebook.com/username/photos/",  # Not a post
            "https://www.facebook.com/groups/123456",  # Group URL
        ],
    )
    def test_invalid_facebook_urls(self, url: str) -> None:
        """Test that invalid Facebook URLs are rejected"""
        result = validate_url(url)
        assert not result.is_valid
        assert result.status == ValidationStatus.INVALID_FORMAT
        assert result.platform == "facebook"

    # Invalid Instagram URLs
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.instagram.com/username/",  # Profile, not post
            "https://www.instagram.com/",  # Root URL
            "https://www.instagram.com/explore/",  # Explore page
        ],
    )
    def test_invalid_instagram_urls(self, url: str) -> None:
        """Test that invalid Instagram URLs are rejected"""
        result = validate_url(url)
        assert not result.is_valid
        assert result.status == ValidationStatus.INVALID_FORMAT
        assert result.platform == "instagram"

    # Auth wall detection
    @pytest.mark.parametrize(
        "url,platform",
        [
            ("https://www.facebook.com/login/", "facebook"),
            ("https://www.facebook.com/checkpoint/", "facebook"),
            ("https://m.facebook.com/login?next=something", "facebook"),
            ("https://www.instagram.com/accounts/login/", "instagram"),
            ("https://www.instagram.com/accounts/signin/", "instagram"),
        ],
    )
    def test_auth_wall_detection(self, url: str, platform: str) -> None:
        """Test that authentication walls are detected"""
        result = validate_url(url)
        assert not result.is_valid
        assert result.status == ValidationStatus.REQUIRES_AUTH
        assert result.platform == platform

    # Unknown platforms
    @pytest.mark.parametrize(
        "url",
        [
            "https://www.twitter.com/user/status/123",
            "https://www.youtube.com/watch?v=abc123",
            "https://www.tiktok.com/@user/video/123",
            "https://www.linkedin.com/posts/123",
            "https://example.com/some/path",
        ],
    )
    def test_unknown_platform_urls(self, url: str) -> None:
        """Test that unknown platform URLs are rejected"""
        result = validate_url(url)
        assert not result.is_valid
        assert result.status == ValidationStatus.UNKNOWN_PLATFORM
        assert result.platform is None

    # Invalid inputs
    @pytest.mark.parametrize(
        "url",
        [
            "",
            "   ",
            None,
            123,
            [],
        ],
    )
    def test_invalid_inputs(self, url) -> None:
        """Test that invalid inputs are rejected"""
        result = URLValidator.validate_url(url)
        assert not result.is_valid
        assert result.status == ValidationStatus.INVALID_FORMAT
        assert result.platform is None

    def test_validation_result_is_valid_property(self) -> None:
        """Test ValidationResult.is_valid property"""
        valid_result = ValidationResult(
            status=ValidationStatus.VALID, platform="facebook", message="OK"
        )
        assert valid_result.is_valid

        invalid_result = ValidationResult(
            status=ValidationStatus.INVALID_FORMAT,
            platform="facebook",
            message="Error",
        )
        assert not invalid_result.is_valid

    def test_url_with_extra_whitespace(self) -> None:
        """Test that URLs with extra whitespace are handled"""
        url = "  https://www.facebook.com/user/posts/123  "
        result = validate_url(url)
        assert result.is_valid
        assert result.platform == "facebook"

    def test_case_insensitivity(self) -> None:
        """Test that URL matching is case-insensitive"""
        urls = [
            "https://WWW.FACEBOOK.COM/user/posts/123",
            "https://www.FACEBOOK.com/user/posts/123",
            "HTTPS://www.facebook.com/user/posts/123",
        ]
        for url in urls:
            result = validate_url(url)
            assert result.is_valid
            assert result.platform == "facebook"

    def test_convenience_function(self) -> None:
        """Test that convenience function works correctly"""
        url = "https://www.instagram.com/p/ABC123/"
        result = validate_url(url)
        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert result.platform == "instagram"
