"""
Unit tests for RateLimiter service
"""
import asyncio
from datetime import datetime, timezone

import pytest

from src.services.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test suite for RateLimiter service"""

    def test_rate_limiter_initialization(self) -> None:
        """Test that RateLimiter can be initialized with valid parameters"""
        limiter = RateLimiter(min_delay=3.0, max_delay=5.0)
        assert limiter.min_delay == 3.0
        assert limiter.max_delay == 5.0
        assert limiter.is_first_request is True

    def test_rate_limiter_invalid_delays(self) -> None:
        """Test that RateLimiter raises error for invalid delay values"""
        with pytest.raises(ValueError, match="must be non-negative"):
            RateLimiter(min_delay=-1.0, max_delay=5.0)

        with pytest.raises(ValueError, match="must be non-negative"):
            RateLimiter(min_delay=3.0, max_delay=-1.0)

        with pytest.raises(ValueError, match="must be less than"):
            RateLimiter(min_delay=5.0, max_delay=3.0)

        with pytest.raises(ValueError, match="must be less than"):
            RateLimiter(min_delay=5.0, max_delay=5.0)

    @pytest.mark.asyncio
    async def test_first_request_no_delay(self) -> None:
        """Test that first request has no delay"""
        limiter = RateLimiter(min_delay=3.0, max_delay=5.0)

        assert limiter.is_first_request is True

        start = datetime.now(timezone.utc)
        delay = await limiter.wait()
        end = datetime.now(timezone.utc)

        assert delay == 0.0
        assert (end - start).total_seconds() < 0.1  # Should be instant
        assert limiter.is_first_request is False

    @pytest.mark.asyncio
    async def test_subsequent_requests_have_delay(self) -> None:
        """Test that subsequent requests respect min/max delay"""
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)

        # First request - no delay
        await limiter.wait()

        # Second request - should have delay
        start = datetime.now(timezone.utc)
        delay = await limiter.wait()
        end = datetime.now(timezone.utc)

        actual_delay = (end - start).total_seconds()

        assert delay >= 0.1
        assert delay <= 0.2
        assert actual_delay >= 0.1
        assert actual_delay <= 0.3  # Allow some overhead

    @pytest.mark.asyncio
    async def test_reset_clears_state(self) -> None:
        """Test that reset() clears the limiter state"""
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)

        # Make first request
        await limiter.wait()
        assert limiter.is_first_request is False

        # Reset
        limiter.reset()
        assert limiter.is_first_request is True

        # Next request should have no delay again
        start = datetime.now(timezone.utc)
        delay = await limiter.wait()
        end = datetime.now(timezone.utc)

        assert delay == 0.0
        assert (end - start).total_seconds() < 0.1

    @pytest.mark.asyncio
    async def test_multiple_requests_maintain_delay(self) -> None:
        """Test that multiple consecutive requests all have appropriate delays"""
        limiter = RateLimiter(min_delay=0.05, max_delay=0.1)

        # First request
        first_delay = await limiter.wait()
        assert first_delay == 0.0

        # Next 5 requests should all have delays
        for _ in range(5):
            delay = await limiter.wait()
            assert delay >= 0.05
            assert delay <= 0.1

    @pytest.mark.asyncio
    async def test_delay_is_randomized(self) -> None:
        """Test that delays are randomized within range"""
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2)

        # First request
        await limiter.wait()

        # Collect delays from multiple requests
        delays = []
        for _ in range(10):
            delay = await limiter.wait()
            delays.append(delay)

        # All delays should be in range
        assert all(0.1 <= d <= 0.2 for d in delays)

        # Delays should have some variation (not all the same)
        # Check that we have at least 3 different values
        unique_delays = len(set(round(d, 3) for d in delays))
        assert unique_delays >= 3, "Delays should be randomized"
