"""
URL validation utility for social media platform URLs

Validates Facebook and Instagram URLs according to FR-014.
Detects authentication requirements and invalid URL formats.
"""
import re
from dataclasses import dataclass
from enum import Enum


class ValidationStatus(str, Enum):
    """Validation result status"""

    VALID = "valid"
    INVALID_FORMAT = "invalid_format"
    REQUIRES_AUTH = "requires_auth"
    UNKNOWN_PLATFORM = "unknown_platform"


@dataclass
class ValidationResult:
    """Result of URL validation"""

    status: ValidationStatus
    platform: str | None
    message: str

    @property
    def is_valid(self) -> bool:
        """Check if validation passed"""
        return self.status == ValidationStatus.VALID


class URLValidator:
    """
    Validator for social media platform URLs

    Supports:
    - Facebook post URLs (m.facebook.com, www.facebook.com, facebook.com)
    - Instagram post URLs (instagram.com, www.instagram.com)

    Detects:
    - Invalid URL formats
    - Authentication walls (login_required, checkpoint paths)
    - Unknown platforms
    """

    # Facebook URL patterns
    FACEBOOK_POST_PATTERNS = [
        # Post with username: facebook.com/username/posts/123456
        r"^https?://(?:www\.|m\.)?facebook\.com/[^/]+/posts/\d+",
        # Photo post: facebook.com/photo?fbid=123456 or facebook.com/photo.php?fbid=123456
        r"^https?://(?:www\.|m\.)?facebook\.com/photo(?:\.php)?\?fbid=\d+",
        # Story: facebook.com/story.php?story_fbid=123&id=456
        r"^https?://(?:www\.|m\.)?facebook\.com/story\.php\?story_fbid=\d+&id=\d+",
        # Permalink: facebook.com/permalink.php?story_fbid=123&id=456
        r"^https?://(?:www\.|m\.)?facebook\.com/permalink\.php\?story_fbid=\d+&id=\d+",
    ]

    # Instagram URL patterns
    INSTAGRAM_POST_PATTERNS = [
        # Post: instagram.com/p/ABC123xyz/
        r"^https?://(?:www\.)?instagram\.com/p/[A-Za-z0-9_-]+",
        # Reel: instagram.com/reel/ABC123xyz/
        r"^https?://(?:www\.)?instagram\.com/reel/[A-Za-z0-9_-]+",
    ]

    # Auth wall indicators
    AUTH_INDICATORS = [
        "login",
        "checkpoint",
        "authenticate",
        "signin",
        "/login/",
        "/checkpoint/",
    ]

    @classmethod
    def validate_url(cls, url: str) -> ValidationResult:
        """
        Validate a social media URL

        Args:
            url: The URL to validate

        Returns:
            ValidationResult with status, platform, and message

        Examples:
            >>> result = URLValidator.validate_url("https://facebook.com/user/posts/123")
            >>> result.is_valid
            True
            >>> result.platform
            'facebook'
        """
        if not url or not isinstance(url, str):
            return ValidationResult(
                status=ValidationStatus.INVALID_FORMAT,
                platform=None,
                message="URL must be a non-empty string",
            )

        url = url.strip()
        
        # Check if URL is empty after stripping
        if not url:
            return ValidationResult(
                status=ValidationStatus.INVALID_FORMAT,
                platform=None,
                message="URL must be a non-empty string",
            )

        # Check for authentication walls
        if cls._requires_auth(url):
            platform = cls._detect_platform(url)
            return ValidationResult(
                status=ValidationStatus.REQUIRES_AUTH,
                platform=platform,
                message=f"URL requires authentication ({platform or 'unknown platform'})",
            )

        # Validate Facebook URL
        if cls._is_facebook_url(url):
            if cls._match_facebook_pattern(url):
                return ValidationResult(
                    status=ValidationStatus.VALID,
                    platform="facebook",
                    message="Valid Facebook post URL",
                )
            return ValidationResult(
                status=ValidationStatus.INVALID_FORMAT,
                platform="facebook",
                message="Invalid Facebook post URL format",
            )

        # Validate Instagram URL
        if cls._is_instagram_url(url):
            if cls._match_instagram_pattern(url):
                return ValidationResult(
                    status=ValidationStatus.VALID,
                    platform="instagram",
                    message="Valid Instagram post URL",
                )
            return ValidationResult(
                status=ValidationStatus.INVALID_FORMAT,
                platform="instagram",
                message="Invalid Instagram post URL format",
            )

        # Unknown platform
        return ValidationResult(
            status=ValidationStatus.UNKNOWN_PLATFORM,
            platform=None,
            message="URL does not match any supported platform (Facebook, Instagram)",
        )

    @classmethod
    def _requires_auth(cls, url: str) -> bool:
        """Check if URL contains authentication indicators"""
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in cls.AUTH_INDICATORS)

    @classmethod
    def _detect_platform(cls, url: str) -> str | None:
        """Detect platform from URL (without validating format)"""
        url_lower = url.lower()
        if "facebook.com" in url_lower:
            return "facebook"
        if "instagram.com" in url_lower:
            return "instagram"
        return None

    @classmethod
    def _is_facebook_url(cls, url: str) -> bool:
        """Check if URL is from Facebook domain"""
        return "facebook.com" in url.lower()

    @classmethod
    def _is_instagram_url(cls, url: str) -> bool:
        """Check if URL is from Instagram domain"""
        return "instagram.com" in url.lower()

    @classmethod
    def _match_facebook_pattern(cls, url: str) -> bool:
        """Check if URL matches Facebook post pattern"""
        return any(
            re.match(pattern, url, re.IGNORECASE)
            for pattern in cls.FACEBOOK_POST_PATTERNS
        )

    @classmethod
    def _match_instagram_pattern(cls, url: str) -> bool:
        """Check if URL matches Instagram post pattern"""
        return any(
            re.match(pattern, url, re.IGNORECASE)
            for pattern in cls.INSTAGRAM_POST_PATTERNS
        )


def validate_url(url: str) -> ValidationResult:
    """
    Convenience function to validate a URL

    Args:
        url: The URL to validate

    Returns:
        ValidationResult with status, platform, and message
    """
    return URLValidator.validate_url(url)
