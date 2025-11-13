"""
Retry handler service for handling transient failures

Implements exponential backoff retry strategy for network errors and
other transient failures.
"""
import asyncio
from typing import Any, Callable, Optional, TypeVar

T = TypeVar("T")


class RetryHandler:
    """
    Retry handler with exponential backoff

    Automatically retries failed operations with increasing delays between attempts.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
    ) -> None:
        """
        Initialize retry handler

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Initial delay in seconds before first retry (default: 1.0)
            max_delay: Maximum delay in seconds between retries (default: 60.0)
            exponential_base: Base for exponential backoff calculation (default: 2.0)

        Raises:
            ValueError: If parameters are invalid
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if base_delay < 0:
            raise ValueError("base_delay must be non-negative")
        if max_delay < base_delay:
            raise ValueError("max_delay must be >= base_delay")
        if exponential_base < 1.0:
            raise ValueError("exponential_base must be >= 1.0")

        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given retry attempt using exponential backoff

        Args:
            attempt: The retry attempt number (0-indexed)

        Returns:
            float: Delay in seconds before next retry
        """
        delay = self.base_delay * (self.exponential_base**attempt)
        return min(delay, self.max_delay)

    async def execute_with_retry(
        self,
        func: Callable[..., T],
        *args: Any,
        retry_on_exceptions: Optional[tuple[type[Exception], ...]] = None,
        **kwargs: Any,
    ) -> T:
        """
        Execute function with retry logic

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            retry_on_exceptions: Tuple of exception types to retry on.
                                If None, retries on all exceptions.
            **kwargs: Keyword arguments for func

        Returns:
            T: Result from successful function execution

        Raises:
            Exception: The last exception if all retries fail
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result

            except Exception as e:
                last_exception = e

                # Check if we should retry this exception
                if retry_on_exceptions is not None and not isinstance(e, retry_on_exceptions):
                    # Don't retry this type of exception
                    raise

                # If we've exhausted retries, raise the exception
                if attempt >= self.max_retries:
                    raise

                # Calculate and wait for exponential backoff
                delay = self.calculate_delay(attempt)
                await asyncio.sleep(delay)

        # Should never reach here, but added for type safety
        if last_exception:
            raise last_exception
        raise RuntimeError("Retry logic failed unexpectedly")


class RetryExhausted(Exception):
    """
    Exception raised when retry attempts are exhausted

    Attributes:
        attempts: Number of retry attempts made
        last_exception: The final exception that caused the failure
    """

    def __init__(self, attempts: int, last_exception: Exception) -> None:
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(
            f"Retry exhausted after {attempts} attempts. "
            f"Last error: {type(last_exception).__name__}: {last_exception}"
        )
