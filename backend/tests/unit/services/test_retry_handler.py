"""
Unit tests for RetryHandler service
"""
import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from src.services.retry_handler import RetryExhausted, RetryHandler


class TestRetryHandler:
    """Test suite for RetryHandler service"""

    def test_retry_handler_initialization(self) -> None:
        """Test that RetryHandler can be initialized with valid parameters"""
        handler = RetryHandler(max_retries=3, base_delay=1.0, max_delay=60.0)
        assert handler.max_retries == 3
        assert handler.base_delay == 1.0
        assert handler.max_delay == 60.0
        assert handler.exponential_base == 2.0

    def test_retry_handler_invalid_parameters(self) -> None:
        """Test that RetryHandler raises error for invalid parameters"""
        with pytest.raises(ValueError, match="must be non-negative"):
            RetryHandler(max_retries=-1)

        with pytest.raises(ValueError, match="must be non-negative"):
            RetryHandler(base_delay=-1.0)

        with pytest.raises(ValueError, match="must be >= base_delay"):
            RetryHandler(base_delay=10.0, max_delay=5.0)

        with pytest.raises(ValueError, match="must be >= 1.0"):
            RetryHandler(exponential_base=0.5)

    def test_calculate_delay_exponential_backoff(self) -> None:
        """Test that delay calculation follows exponential backoff"""
        handler = RetryHandler(base_delay=1.0, max_delay=60.0, exponential_base=2.0)

        assert handler.calculate_delay(0) == 1.0  # 1 * 2^0
        assert handler.calculate_delay(1) == 2.0  # 1 * 2^1
        assert handler.calculate_delay(2) == 4.0  # 1 * 2^2
        assert handler.calculate_delay(3) == 8.0  # 1 * 2^3

    def test_calculate_delay_respects_max_delay(self) -> None:
        """Test that delay calculation never exceeds max_delay"""
        handler = RetryHandler(base_delay=1.0, max_delay=10.0, exponential_base=2.0)

        assert handler.calculate_delay(0) == 1.0
        assert handler.calculate_delay(1) == 2.0
        assert handler.calculate_delay(2) == 4.0
        assert handler.calculate_delay(3) == 8.0
        assert handler.calculate_delay(4) == 10.0  # Capped at max_delay
        assert handler.calculate_delay(5) == 10.0  # Still capped
        assert handler.calculate_delay(10) == 10.0  # Still capped

    @pytest.mark.asyncio
    async def test_execute_with_retry_succeeds_first_attempt(self) -> None:
        """Test that successful functions execute without retry"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)

        async def successful_func() -> str:
            return "success"

        result = await handler.execute_with_retry(successful_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_execute_with_retry_succeeds_after_failures(self) -> None:
        """Test that function succeeds after some failures"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)
        mock_func = AsyncMock()

        # Fail twice, then succeed
        mock_func.side_effect = [
            RuntimeError("First failure"),
            RuntimeError("Second failure"),
            "success",
        ]

        result = await handler.execute_with_retry(mock_func)
        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_with_retry_exhausts_retries(self) -> None:
        """Test that retry raises exception after max retries exhausted"""
        handler = RetryHandler(max_retries=2, base_delay=0.01)
        mock_func = AsyncMock()

        # Always fail
        mock_func.side_effect = RuntimeError("Persistent failure")

        with pytest.raises(RuntimeError, match="Persistent failure"):
            await handler.execute_with_retry(mock_func)

        # Should try: initial + 2 retries = 3 times
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_with_retry_specific_exceptions(self) -> None:
        """Test that retry only happens for specific exception types"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)
        mock_func = AsyncMock()

        # Throw an exception that we're NOT retrying on
        mock_func.side_effect = ValueError("Should not retry")

        with pytest.raises(ValueError, match="Should not retry"):
            await handler.execute_with_retry(
                mock_func,
                retry_on_exceptions=(RuntimeError,),  # Only retry RuntimeError
            )

        # Should only try once (no retries for ValueError)
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_with_retry_multiple_exception_types(self) -> None:
        """Test that retry works for multiple exception types"""
        handler = RetryHandler(max_retries=3, base_delay=0.01)
        mock_func = AsyncMock()

        # Throw different retriable exceptions, then succeed
        mock_func.side_effect = [
            RuntimeError("Runtime error"),
            ConnectionError("Connection error"),
            "success",
        ]

        result = await handler.execute_with_retry(
            mock_func,
            retry_on_exceptions=(RuntimeError, ConnectionError),
        )

        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_with_retry_waits_with_backoff(self) -> None:
        """Test that retry handler waits with exponential backoff"""
        handler = RetryHandler(max_retries=2, base_delay=0.05, exponential_base=2.0)
        mock_func = AsyncMock()
        mock_func.side_effect = [
            RuntimeError("First"),
            RuntimeError("Second"),
            "success",
        ]

        import time

        start = time.time()
        result = await handler.execute_with_retry(mock_func)
        duration = time.time() - start

        assert result == "success"
        # Total wait: 0.05 (attempt 0) + 0.10 (attempt 1) = 0.15 seconds
        # Allow some overhead
        assert duration >= 0.15
        assert duration < 0.25

    @pytest.mark.asyncio
    async def test_execute_with_retry_passes_arguments(self) -> None:
        """Test that arguments are correctly passed to the function"""
        handler = RetryHandler(max_retries=1, base_delay=0.01)

        async def func_with_args(a: int, b: int, c: str = "default") -> str:
            return f"{a}+{b}={a+b},{c}"

        result = await handler.execute_with_retry(func_with_args, 1, 2, c="custom")
        assert result == "1+2=3,custom"

    def test_retry_exhausted_exception(self) -> None:
        """Test RetryExhausted exception formatting"""
        original_error = RuntimeError("Original error")
        retry_error = RetryExhausted(attempts=3, last_exception=original_error)

        assert retry_error.attempts == 3
        assert retry_error.last_exception is original_error
        assert "3 attempts" in str(retry_error)
        assert "RuntimeError" in str(retry_error)
        assert "Original error" in str(retry_error)
