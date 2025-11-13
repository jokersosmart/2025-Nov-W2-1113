"""
Facebook scraper service using Playwright

Scrapes comments from public Facebook posts with rate limiting and error handling.
"""
import asyncio
import re
from datetime import datetime, timezone
from typing import Any

from playwright.async_api import Page, async_playwright

from src.models.comment import Comment
from src.models.post import Platform, Post
from src.services.rate_limiter import RateLimiter
from src.services.retry_handler import RetryHandler


class FacebookScraperError(Exception):
    """Base exception for Facebook scraper errors"""

    pass


class FacebookAuthRequired(FacebookScraperError):
    """Raised when Facebook requires authentication"""

    pass


class FacebookScraper:
    """
    Facebook post and comment scraper

    Uses Playwright to scrape public Facebook posts and their comments.
    Implements rate limiting and retry logic for reliability.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter | None = None,
        retry_handler: RetryHandler | None = None,
        headless: bool = True,
    ):
        """
        Initialize Facebook scraper

        Args:
            rate_limiter: Rate limiter for controlling request speed (default: 3-5s)
            retry_handler: Retry handler for network errors (default: 3 retries)
            headless: Run browser in headless mode
        """
        self.rate_limiter = rate_limiter or RateLimiter(min_delay=3.0, max_delay=5.0)
        self.retry_handler = retry_handler or RetryHandler(max_retries=3)
        self.headless = headless

    async def scrape_post(self, post_url: str) -> Post:
        """
        Scrape post information from Facebook

        Args:
            post_url: Facebook post URL

        Returns:
            Post object with scraped data

        Raises:
            FacebookAuthRequired: If authentication is required
            FacebookScraperError: If scraping fails
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            try:
                page = await browser.new_page()
                await self.rate_limiter.wait()

                # Navigate to post
                await self.retry_handler.execute_with_retry(
                    page.goto,
                    post_url,
                    wait_until="domcontentloaded",
                    retry_on_exceptions=(Exception,),
                )

                # Check for auth wall
                if await self._check_auth_required(page):
                    raise FacebookAuthRequired("Login required to access this post")

                # Extract post data
                post_data = await self._extract_post_data(page, post_url)
                return Post(**post_data)
            finally:
                await browser.close()

    async def scrape_comments(
        self, post_url: str, progress_callback: Any = None
    ) -> list[Comment]:
        """
        Scrape all first-level comments from a Facebook post

        Args:
            post_url: Facebook post URL
            progress_callback: Optional callback function for progress updates
                               callback(current, total, message)

        Returns:
            List of Comment objects

        Raises:
            FacebookAuthRequired: If authentication is required
            FacebookScraperError: If scraping fails
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            try:
                page = await browser.new_page()
                await self.rate_limiter.wait()

                # Navigate to post
                await self.retry_handler.execute_with_retry(
                    page.goto,
                    post_url,
                    wait_until="domcontentloaded",
                    retry_on_exceptions=(Exception,),
                )

                # Check for auth wall
                if await self._check_auth_required(page):
                    raise FacebookAuthRequired("Login required to access this post")

                # Expand all comments
                await self._expand_comments(page, progress_callback)

                # Extract comments
                comments = await self._extract_comments(page, post_url)

                if progress_callback:
                    progress_callback(len(comments), len(comments), "Scraping complete")

                return comments
            finally:
                await browser.close()

    async def _check_auth_required(self, page: Page) -> bool:
        """Check if page requires authentication"""
        # Check URL for login indicators
        current_url = page.url
        auth_indicators = ["login", "checkpoint", "authenticate"]
        if any(indicator in current_url.lower() for indicator in auth_indicators):
            return True

        # Check for login dialog
        login_selectors = [
            'a[href*="login"]',
            'button:has-text("Log In")',
            'div:has-text("Log in to continue")',
        ]
        for selector in login_selectors:
            try:
                if await page.locator(selector).first.is_visible(timeout=2000):
                    return True
            except Exception:
                continue

        return False

    async def _extract_post_data(self, page: Page, post_url: str) -> dict[str, Any]:
        """Extract post information from page"""
        post_data = {
            "platform": Platform.FACEBOOK,
            "post_url": post_url,
            "post_time": datetime.now(timezone.utc).isoformat(),
            "post_content": "",
            "likes_count": 0,
            "comments_count": 0,
        }

        # Extract post content
        content_selectors = [
            '[data-ad-preview="message"]',
            '[data-testid="post_message"]',
            ".userContent",
            '[role="article"] div[dir="auto"]',
        ]
        for selector in content_selectors:
            try:
                content = await page.locator(selector).first.inner_text(timeout=3000)
                if content:
                    post_data["post_content"] = content.strip()[:10000]
                    break
            except Exception:
                continue

        # Extract likes count
        likes_selectors = [
            '[aria-label*="Like"]',
            '[aria-label*="reaction"]',
            'span:has-text("Like")',
        ]
        for selector in likes_selectors:
            try:
                likes_text = await page.locator(selector).first.inner_text(timeout=2000)
                likes_match = re.search(r"(\d+)", likes_text.replace(",", ""))
                if likes_match:
                    post_data["likes_count"] = int(likes_match.group(1))
                    break
            except Exception:
                continue

        # Extract comments count
        comments_selectors = [
            '[aria-label*="comment"]',
            'span:has-text("comment")',
        ]
        for selector in comments_selectors:
            try:
                comments_text = await page.locator(selector).first.inner_text(
                    timeout=2000
                )
                comments_match = re.search(r"(\d+)", comments_text.replace(",", ""))
                if comments_match:
                    post_data["comments_count"] = int(comments_match.group(1))
                    break
            except Exception:
                continue

        return post_data

    async def _expand_comments(self, page: Page, progress_callback: Any = None) -> None:
        """Expand all collapsed comments"""
        # Click "View more comments" buttons
        more_comments_selectors = [
            'div:has-text("View more comments")',
            'span:has-text("View more comments")',
            '[role="button"]:has-text("more comment")',
        ]

        max_iterations = 50  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            found_button = False
            for selector in more_comments_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=1000):
                        await button.click()
                        await asyncio.sleep(1)  # Wait for comments to load
                        found_button = True
                        iteration += 1

                        if progress_callback:
                            progress_callback(
                                iteration, max_iterations, "Loading more comments..."
                            )
                        break
                except Exception:
                    continue

            if not found_button:
                break

            await self.rate_limiter.wait()

    async def _extract_comments(self, page: Page, post_url: str) -> list[Comment]:
        """Extract comment data from page"""
        comments = []

        # Find all comment elements
        comment_selectors = [
            '[role="article"]',
            ".UFIComment",
            '[data-testid^="UFI2Comment"]',
        ]

        for selector in comment_selectors:
            try:
                comment_elements = await page.locator(selector).all()
                if comment_elements:
                    break
            except Exception:
                continue
        else:
            comment_elements = []

        for idx, element in enumerate(comment_elements):
            try:
                comment_data = await self._extract_single_comment(
                    element, post_url, idx
                )
                if comment_data:
                    comments.append(Comment(**comment_data))
            except Exception:
                # Skip invalid comments
                continue

        return comments

    async def _extract_single_comment(
        self, element: Any, post_url: str, index: int
    ) -> dict[str, Any] | None:
        """Extract single comment data"""
        try:
            # Extract commenter ID/name
            commenter_id = "unknown"
            try:
                commenter_link = await element.locator("a[href*='/']").first.get_attribute(
                    "href", timeout=1000
                )
                if commenter_link:
                    match = re.search(r"/([^/?]+)", commenter_link)
                    if match:
                        commenter_id = match.group(1)
            except Exception:
                pass

            # Extract comment content
            comment_content = ""
            content_selectors = ['div[dir="auto"]', "span", ".comment-content"]
            for selector in content_selectors:
                try:
                    content = await element.locator(selector).first.inner_text(
                        timeout=1000
                    )
                    if content and len(content) > 5:
                        comment_content = content.strip()[:5000]
                        break
                except Exception:
                    continue

            if not comment_content:
                return None

            # Extract timestamp (default to now if not found)
            comment_time = datetime.now(timezone.utc).isoformat()
            try:
                time_element = await element.locator("abbr, time").first.get_attribute(
                    "data-utime", timeout=1000
                )
                if time_element:
                    comment_time = datetime.fromtimestamp(
                        int(time_element), tz=timezone.utc
                    ).isoformat()
            except Exception:
                pass

            return {
                "comment_id": f"fb_{index}_{hash(comment_content) % 100000}",
                "post_url": post_url,
                "comment_time": comment_time,
                "commenter_id": commenter_id,
                "comment_content": comment_content,
            }
        except Exception:
            return None
