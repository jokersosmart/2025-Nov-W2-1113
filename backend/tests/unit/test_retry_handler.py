"""
Unit tests for retry handler

Tests retry logic with exponential backoff following TDD principles.
"""
import asyncio

import pytest

from src.api.middleware.error_handler import NetworkError, RateLimitError
from src.services.retry_handler import RetryExhausted, RetryHandler


class TestRetryHandlerInit:
    """Test RetryHandler initialization"""

    def test_default_initialization(self):
        """Should create handler with default parameters"""
        handler = RetryHandler()

        assert handler.max_retries == 3
        assert handler.base_delay == 1.0
        assert handler.max_delay == 60.0
        assert handler.exponential_base == 2.0

    def test_custom_initialization(self):
        """Should create handler with custom parameters"""
        handler = RetryHandler(
            max_retries=5, base_delay=2.0, max_delay=120.0, exponential_base=3.0
        )

        assert handler.max_retries == 5
        assert handler.base_delay == 2.0
        assert handler.max_delay == 120.0
        assert handler.exponential_base == 3.0

    def test_invalid_max_retries(self):
        """Should raise ValueError for negative max_retries"""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            RetryHandler(max_retries=-1)

    def test_invalid_base_delay(self):
        """Should raise ValueError for negative base_delay"""
        with pytest.raises(ValueError, match="base_delay must be non-negative"):
            RetryHandler(base_delay=-1.0)

    def test_invalid_max_delay(self):
        """Should raise ValueError if max_delay < base_delay"""
        with pytest.raises(ValueError, match="max_delay must be >= base_delay"):
            RetryHandler(base_delay=10.0, max_delay=5.0)

    def test_invalid_exponential_base(self):
        """Should raise ValueError for exponential_base < 1.0"""
        with pytest.raises(ValueError, match="exponential_base must be >= 1.0"):
            RetryHandler(exponential_base=0.5)


class TestExponentialBackoff:
    """Test exponential backoff calculation"""

    def test_calculate_delay_first_attempt(self):
        """First retry should use base_delay"""
        handler = RetryHandler(base_delay=1.0, exponential_base=2.0)

        delay = handler.calculate_delay(0)
        assert delay == 1.0

    def test_calculate_delay_second_attempt(self):
        """Second retry should double the delay"""
        handler = RetryHandler(base_delay=1.0, exponential_base=2.0)

        delay = handler.calculate_delay(1)
        assert delay == 2.0

    def test_calculate_delay_third_attempt(self):
        """Third retry should quadruple the delay"""
        handler = RetryHandler(base_delay=1.0, exponential_base=2.0)

        delay = handler.calculate_delay(2)
        assert delay == 4.0

    def test_calculate_delay_respects_max(self):
        """Delay should not exceed max_delay"""
        handler = RetryHandler(base_delay=1.0, max_delay=5.0, exponential_base=2.0)

        # 2^10 = 1024 but max is 5.0
        delay = handler.calculate_delay(10)
        assert delay == 5.0

    def test_calculate_delay_custom_base(self):
        """Should work with custom exponential base"""
        handler = RetryHandler(base_delay=1.0, exponential_base=3.0)

        assert handler.calculate_delay(0) == 1.0  # 1.0 * 3^0
        assert handler.calculate_delay(1) == 3.0  # 1.0 * 3^1
        assert handler.calculate_delay(2) == 9.0  # 1.0 * 3^2


class TestRetryExecution:
    """Test retry execution logic"""

    @pytest.mark.asyncio
    async def test_successful_first_attempt(self):
        """Should return result on first successful attempt"""
        handler = RetryHandler()
        call_count = 0

        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await handler.execute_with_retry(success_func)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self):
        """Should retry on transient failure and eventually succeed"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)
        call_count = 0

        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        result = await handler.execute_with_retry(flaky_func)

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Should raise original exception when retries exhausted"""
        handler = RetryHandler(max_retries=2, base_delay=0.01)
        call_count = 0

        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise NetworkError("Persistent failure")

        with pytest.raises(NetworkError, match="Persistent failure"):
            await handler.execute_with_retry(always_fails)

        # Should try 1 initial + 2 retries = 3 times
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_specific_exceptions(self):
        """Should only retry on specified exception types"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)
        call_count = 0

        async def fails_with_network_error():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise NetworkError("Retry this")
            else:
                raise ValueError("Don't retry this")

        # Should retry NetworkError but not ValueError
        with pytest.raises(ValueError, match="Don't retry this"):
            await handler.execute_with_retry(
                fails_with_network_error, retry_on_exceptions=(NetworkError,)
            )

        assert call_count == 2  # Initial + 1 retry, then different exception

    @pytest.mark.asyncio
    async def test_no_retry_on_rate_limit_error(self):
        """Should not retry RateLimitError"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)
        call_count = 0

        async def rate_limited():
            nonlocal call_count
            call_count += 1
            raise RateLimitError("Rate limited", retry_after=60)

        with pytest.raises(RateLimitError):
            await handler.execute_with_retry(
                rate_limited, retry_on_exceptions=(NetworkError,)
            )

        # Should fail immediately without retry
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_function_with_args_and_kwargs(self):
        """Should pass args and kwargs to function"""
        handler = RetryHandler()

        async def func_with_params(x, y, z=0):
            return x + y + z

        result = await handler.execute_with_retry(func_with_params, 1, 2, z=3)
        assert result == 6

    @pytest.mark.asyncio
    async def test_sync_function_execution(self):
        """Should handle synchronous functions"""
        handler = RetryHandler()

        def sync_func():
            return "sync_result"

        result = await handler.execute_with_retry(sync_func)
        assert result == "sync_result"


class TestRetryBackoffTiming:
    """Test actual timing of retry delays"""

    @pytest.mark.asyncio
    async def test_delay_increases_exponentially(self):
        """Should wait exponentially longer between retries"""
        handler = RetryHandler(max_retries=3, base_delay=0.1, exponential_base=2.0)
        call_times = []

        async def track_timing():
            call_times.append(asyncio.get_event_loop().time())
            if len(call_times) < 3:
                raise NetworkError("Fail")
            return "success"

        await handler.execute_with_retry(track_timing)

        # Check delays between calls
        # First retry: ~0.1s delay (2^0 * 0.1)
        # Second retry: ~0.2s delay (2^1 * 0.1)
        assert len(call_times) == 3
        first_delay = call_times[1] - call_times[0]
        second_delay = call_times[2] - call_times[1]

        # Allow 50ms tolerance
        assert 0.05 < first_delay < 0.15
        assert 0.15 < second_delay < 0.25


class TestRetryExhausted:
    """Test RetryExhausted exception"""

    def test_retry_exhausted_creation(self):
        """Should create RetryExhausted with details"""
        original_error = NetworkError("Connection failed")
        exc = RetryExhausted(attempts=3, last_exception=original_error)

        assert exc.attempts == 3
        assert exc.last_exception is original_error
        assert "3 attempts" in str(exc)
        assert "NetworkError" in str(exc)


class TestEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.mark.asyncio
    async def test_zero_retries(self):
        """max_retries=0 should not retry"""
        handler = RetryHandler(max_retries=0)
        call_count = 0

        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise NetworkError("Fail")

        with pytest.raises(NetworkError):
            await handler.execute_with_retry(always_fails)

        assert call_count == 1  # No retries

    @pytest.mark.asyncio
    async def test_exception_with_no_message(self):
        """Should handle exceptions without messages"""
        handler = RetryHandler(max_retries=1, base_delay=0.01)

        async def raises_empty():
            raise ValueError()

        with pytest.raises(ValueError):
            await handler.execute_with_retry(raises_empty)

    @pytest.mark.asyncio
    async def test_retry_all_exceptions_when_none_specified(self):
        """Should retry all exceptions when retry_on_exceptions is None"""
        handler = RetryHandler(max_retries=2, base_delay=0.01)
        call_count = 0

        async def various_errors():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First error")
            elif call_count == 2:
                raise TypeError("Second error")
            return "success"

        result = await handler.execute_with_retry(various_errors)

        assert result == "success"
        assert call_count == 3
