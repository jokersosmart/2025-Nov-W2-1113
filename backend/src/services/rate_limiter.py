"""
Rate limiter service for controlling scraping speed

Implements conservative rate limiting strategy to avoid platform restrictions.
Default: 3-5 seconds interval between batches.
"""
import asyncio
from random import uniform
from typing import Optional


class RateLimiter:
    """
    Rate limiter to control request frequency

    Uses randomized delays between min and max values to appear more natural
    and avoid detection patterns.
    """

    def __init__(
        self,
        min_delay: float = 3.0,
        max_delay: float = 5.0,
    ) -> None:
        """
        Initialize rate limiter

        Args:
            min_delay: Minimum delay in seconds between requests (default: 3.0)
            max_delay: Maximum delay in seconds between requests (default: 5.0)

        Raises:
            ValueError: If min_delay >= max_delay or delays are negative
        """
        if min_delay < 0 or max_delay < 0:
            raise ValueError("Delays must be non-negative")
        if min_delay >= max_delay:
            raise ValueError("min_delay must be less than max_delay")

        self.min_delay = min_delay
        self.max_delay = max_delay
        self._last_request_time: Optional[float] = None

    async def wait(self) -> float:
        """
        Wait for appropriate delay before next request

        Returns:
            float: Actual delay time in seconds

        Note:
            First call (when _last_request_time is None) returns immediately
        """
        if self._last_request_time is None:
            # First request - no delay needed
            self._last_request_time = asyncio.get_event_loop().time()
            return 0.0

        # Calculate randomized delay
        delay = uniform(self.min_delay, self.max_delay)

        # Wait for the delay
        await asyncio.sleep(delay)

        # Update last request time
        self._last_request_time = asyncio.get_event_loop().time()

        return delay

    def reset(self) -> None:
        """
        Reset the rate limiter

        Useful when starting a new scraping session or after an error
        """
        self._last_request_time = None

    @property
    def is_first_request(self) -> bool:
        """
        Check if this is the first request (no delay needed)

        Returns:
            bool: True if no requests have been made yet
        """
        return self._last_request_time is None
