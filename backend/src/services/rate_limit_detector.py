"""
Rate limit detection module

Detects rate limiting signals from social media platforms including:
- HTTP status codes (429)
- Response headers (Retry-After, X-RateLimit-*)
- Page content (checkpoint pages, CAPTCHA, error messages)
- URL patterns (challenge, checkpoint)

Usage:
    # Check HTTP response
    response = await page.goto(url)
    is_limited, retry_after = detect_rate_limit(response)
    if is_limited:
        raise RateLimitError(f"Rate limited, retry after {retry_after}s")

    # Check page content
    if await detect_rate_limit_from_page(page):
        raise RateLimitError("Rate limit detected in page content")

    # Convenience functions that raise automatically
    check_rate_limit(response)  # Raises RateLimitError if detected
    await check_page_rate_limit(page)  # Raises RateLimitError if detected
"""
import re
from typing import Any

from playwright.async_api import Page, Response

from src.api.middleware.error_handler import RateLimitError


def detect_rate_limit(response: Response | Any) -> tuple[bool, int]:
    """
    Detect rate limiting from HTTP response

    Args:
        response: HTTP response object (Playwright Response or similar)

    Returns:
        Tuple of (is_rate_limited: bool, retry_after_seconds: int)
    """
    # Check HTTP status code
    if hasattr(response, "status") and response.status == 429:
        retry_after = _parse_retry_after(response)
        return True, retry_after

    # Check X-RateLimit headers
    if hasattr(response, "headers"):
        headers = response.headers if isinstance(response.headers, dict) else {}

        # X-RateLimit-Remaining: 0 indicates rate limit
        remaining = headers.get("x-ratelimit-remaining") or headers.get(
            "X-RateLimit-Remaining"
        )
        if remaining is not None:
            try:
                if int(remaining) == 0:
                    reset_time = headers.get("x-ratelimit-reset") or headers.get(
                        "X-RateLimit-Reset"
                    )
                    retry_after = _calculate_retry_from_reset(reset_time)
                    return True, retry_after
            except (ValueError, TypeError):
                pass

    return False, 0


def _parse_retry_after(response: Response | Any) -> int:
    """Parse Retry-After header from response"""
    if not hasattr(response, "headers"):
        return 60  # Default 60 seconds

    headers = response.headers if isinstance(response.headers, dict) else {}
    retry_after = headers.get("retry-after") or headers.get("Retry-After")

    if retry_after:
        try:
            # Try to parse as integer (seconds)
            return int(retry_after)
        except ValueError:
            # Might be HTTP date format, default to 60s
            return 60

    return 60  # Default if not specified


def _calculate_retry_from_reset(reset_time: str | None) -> int:
    """Calculate retry seconds from X-RateLimit-Reset timestamp"""
    if not reset_time:
        return 60

    try:
        import time

        reset_timestamp = int(reset_time)
        current_timestamp = int(time.time())
        retry_seconds = max(reset_timestamp - current_timestamp, 60)
        return min(retry_seconds, 3600)  # Cap at 1 hour
    except (ValueError, TypeError):
        return 60


async def detect_rate_limit_from_page(page: Page) -> bool:
    """
    Detect rate limiting from page content and URL

    Checks for:
    - Challenge/checkpoint URLs
    - Rate limit keywords in content
    - CAPTCHA presence
    - Error messages

    Args:
        page: Playwright Page object

    Returns:
        True if rate limit detected, False otherwise
    """
    # Check URL patterns
    url = page.url.lower()
    rate_limit_url_patterns = [
        "/checkpoint/",
        "/challenge/",
        "/security/",
        "/verify/",
        "suspicious_login",
        "confirm_identity",
    ]

    for pattern in rate_limit_url_patterns:
        if pattern in url:
            return True

    # Check page content
    try:
        content = await page.content()
        content_lower = content.lower()

        # Rate limit keywords
        rate_limit_keywords = [
            "too many requests",
            "rate limit",
            "temporarily blocked",
            "try again later",
            "suspicious activity",
            "unusual activity",
            "slow down",
            "please wait",
            "throttled",
            "頻繁存取",  # Chinese: frequent access
            "請稍後再試",  # Chinese: please try again later
            "暫時封鎖",  # Chinese: temporarily blocked
        ]

        for keyword in rate_limit_keywords:
            if keyword in content_lower:
                return True

        # Check for CAPTCHA
        captcha_indicators = [
            "g-recaptcha",
            "recaptcha",
            "captcha",
            "hcaptcha",
            'id="captcha"',
            'class="captcha"',
        ]

        for indicator in captcha_indicators:
            if indicator in content_lower:
                return True

    except Exception:
        # If we can't read content, assume no rate limit
        pass

    return False


def check_rate_limit(response: Response | Any) -> None:
    """
    Check response for rate limiting and raise error if detected

    Args:
        response: HTTP response object

    Raises:
        RateLimitError: If rate limit is detected
    """
    is_limited, retry_after = detect_rate_limit(response)
    if is_limited:
        raise RateLimitError(
            message="平台偵測到頻繁存取,請稍後再試", retry_after=retry_after
        )


async def check_page_rate_limit(page: Page) -> None:
    """
    Check page content for rate limiting and raise error if detected

    Args:
        page: Playwright Page object

    Raises:
        RateLimitError: If rate limit is detected
    """
    if await detect_rate_limit_from_page(page):
        raise RateLimitError(message="平台偵測到頻繁存取,請稍後再試", retry_after=60)


# Convenience function for scraper integration
async def check_response_and_page(response: Response | Any, page: Page) -> None:
    """
    Check both HTTP response and page content for rate limiting

    Args:
        response: HTTP response object
        page: Playwright Page object

    Raises:
        RateLimitError: If rate limit is detected in either
    """
    # Check response first (faster)
    check_rate_limit(response)

    # Then check page content
    await check_page_rate_limit(page)
