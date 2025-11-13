"""
Instagram scraper service using Playwright

Scrapes comments from public Instagram posts with rate limiting and error handling.
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


class InstagramScraperError(Exception):
    """Base exception for Instagram scraper errors"""

    pass


class InstagramAuthRequired(InstagramScraperError):
    """Raised when Instagram requires authentication"""

    pass


class InstagramScraper:
    """
    Instagram post and comment scraper

    Uses Playwright to scrape public Instagram posts and their comments.
    Implements rate limiting and retry logic for reliability.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter | None = None,
        retry_handler: RetryHandler | None = None,
        headless: bool = True,
    ):
        """
        Initialize Instagram scraper

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
        Scrape post information from Instagram

        Args:
            post_url: Instagram post URL

        Returns:
            Post object with scraped data

        Raises:
            InstagramAuthRequired: If authentication is required
            InstagramScraperError: If scraping fails
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
                    raise InstagramAuthRequired("Login required to access this post")

                # Extract post data
                post_data = await self._extract_post_data(page, post_url)
                return Post(**post_data)
            finally:
                await browser.close()

    async def scrape_comments(
        self, post_url: str, progress_callback: Any = None
    ) -> list[Comment]:
        """
        Scrape all first-level comments from an Instagram post

        Args:
            post_url: Instagram post URL
            progress_callback: Optional callback function for progress updates

        Returns:
            List of Comment objects

        Raises:
            InstagramAuthRequired: If authentication is required
            InstagramScraperError: If scraping fails
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
                    raise InstagramAuthRequired("Login required to access this post")

                # Load more comments
                await self._load_more_comments(page, progress_callback)

                # Extract comments
                comments = await self._extract_comments(page, post_url)

                if progress_callback:
                    progress_callback(len(comments), len(comments), "Scraping complete")

                return comments
            finally:
                await browser.close()

    async def _check_auth_required(self, page: Page) -> bool:
        """Check if page requires authentication"""
        current_url = page.url
        auth_indicators = ["accounts/login", "accounts/signin"]
        if any(indicator in current_url.lower() for indicator in auth_indicators):
            return True

        # Check for login prompt
        login_selectors = ['a[href*="accounts/login"]', 'button:has-text("Log In")']
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
            "platform": Platform.INSTAGRAM,
            "post_url": post_url,
            "post_time": datetime.now(timezone.utc).isoformat(),
            "post_content": "",
            "likes_count": 0,
            "comments_count": 0,
        }

        # Extract post caption
        caption_selectors = [
            'h1._aacl._aaco._aacu._aacx._aad7._aade',
            'span._ac2a',
            'div._a9zs span',
        ]
        for selector in caption_selectors:
            try:
                content = await page.locator(selector).first.inner_text(timeout=3000)
                if content:
                    post_data["post_content"] = content.strip()[:10000]
                    break
            except Exception:
                continue

        # Extract likes count
        try:
            likes_text = await page.locator(
                'section span a:has-text("like")'
            ).first.inner_text(timeout=2000)
            likes_match = re.search(r"([\d,]+)", likes_text)
            if likes_match:
                post_data["likes_count"] = int(likes_match.group(1).replace(",", ""))
        except Exception:
            pass

        # Extract comments count
        try:
            comments_button = await page.locator(
                'a:has-text("comment")'
            ).first.inner_text(timeout=2000)
            comments_match = re.search(r"([\d,]+)", comments_button)
            if comments_match:
                post_data["comments_count"] = int(
                    comments_match.group(1).replace(",", "")
                )
        except Exception:
            pass

        return post_data

    async def _load_more_comments(
        self, page: Page, progress_callback: Any = None
    ) -> None:
        """Load more comments by clicking load more button"""
        max_iterations = 50
        iteration = 0

        while iteration < max_iterations:
            try:
                load_more_button = page.locator('button:has-text("Load more comments")')
                if await load_more_button.is_visible(timeout=1000):
                    await load_more_button.click()
                    await asyncio.sleep(1)
                    iteration += 1

                    if progress_callback:
                        progress_callback(
                            iteration, max_iterations, "Loading more comments..."
                        )

                    await self.rate_limiter.wait()
                else:
                    break
            except Exception:
                break

    async def _extract_comments(self, page: Page, post_url: str) -> list[Comment]:
        """Extract comment data from page"""
        comments = []

        # Find all comment elements
        comment_selectors = ['ul._a9z6._a9za li', 'div[role="button"] span._a9zr']

        for selector in comment_selectors:
            try:
                comment_elements = await page.locator(selector).all()
                if comment_elements and len(comment_elements) > 0:
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
                continue

        return comments

    async def _extract_single_comment(
        self, element: Any, post_url: str, index: int
    ) -> dict[str, Any] | None:
        """Extract single comment data"""
        try:
            # Extract commenter ID
            commenter_id = "unknown"
            try:
                commenter_link = await element.locator("a").first.get_attribute(
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
            try:
                content = await element.locator("span").inner_text(timeout=1000)
                if content and len(content) > 3:
                    comment_content = content.strip()[:5000]
            except Exception:
                pass

            if not comment_content:
                return None

            # Use current time as fallback for timestamp
            comment_time = datetime.now(timezone.utc).isoformat()

            return {
                "comment_id": f"ig_{index}_{hash(comment_content) % 100000}",
                "post_url": post_url,
                "comment_time": comment_time,
                "commenter_id": commenter_id,
                "comment_content": comment_content,
            }
        except Exception:
            return None
