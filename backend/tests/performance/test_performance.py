"""
Performance validation tests

Quick smoke tests to verify basic performance characteristics
without running full Locust load tests.
"""
import asyncio
import time

import pytest
from fastapi.testclient import TestClient

from main import app


class TestAPIPerformance:
    """Test basic API performance"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_check_response_time(self, client):
        """Health check should respond in < 50ms"""
        times = []

        for _ in range(10):
            start = time.perf_counter()
            response = client.get("/health")
            end = time.perf_counter()

            assert response.status_code == 200
            times.append((end - start) * 1000)  # Convert to ms

        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]

        print(f"\nHealth check - Avg: {avg_time:.2f}ms, p95: {p95_time:.2f}ms")

        # Should be very fast
        assert avg_time < 50, f"Average response time {avg_time:.2f}ms exceeds 50ms"
        assert (
            p95_time < 100
        ), f"p95 response time {p95_time:.2f}ms exceeds 100ms"

    def test_root_endpoint_response_time(self, client):
        """Root endpoint should respond in < 100ms"""
        times = []

        for _ in range(10):
            start = time.perf_counter()
            response = client.get("/")
            end = time.perf_counter()

            assert response.status_code == 200
            times.append((end - start) * 1000)

        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]

        print(f"\nRoot endpoint - Avg: {avg_time:.2f}ms, p95: {p95_time:.2f}ms")

        assert avg_time < 100, f"Average response time {avg_time:.2f}ms exceeds 100ms"
        assert (
            p95_time < 200
        ), f"p95 response time {p95_time:.2f}ms exceeds 200ms"

    def test_openapi_schema_response_time(self, client):
        """OpenAPI schema should respond in < 200ms"""
        times = []

        for _ in range(5):
            start = time.perf_counter()
            response = client.get("/openapi.json")
            end = time.perf_counter()

            assert response.status_code == 200
            times.append((end - start) * 1000)

        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]

        print(f"\nOpenAPI schema - Avg: {avg_time:.2f}ms, p95: {p95_time:.2f}ms")

        assert (
            avg_time < 200
        ), f"Average response time {avg_time:.2f}ms exceeds 200ms"
        assert (
            p95_time < 500
        ), f"p95 response time {p95_time:.2f}ms exceeds 500ms"

    def test_invalid_scrape_request_response_time(self, client):
        """Invalid scrape request should fail fast (< 200ms)"""
        times = []

        for _ in range(10):
            start = time.perf_counter()
            response = client.post(
                "/api/scrape",
                json={"url": "invalid-url", "platform": "facebook"},
            )
            end = time.perf_counter()

            # Should return validation error
            assert response.status_code in [400, 422]
            times.append((end - start) * 1000)

        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]

        print(
            f"\nInvalid scrape request - Avg: {avg_time:.2f}ms, p95: {p95_time:.2f}ms"
        )

        # Validation should be fast
        assert (
            avg_time < 100
        ), f"Average response time {avg_time:.2f}ms exceeds 100ms"
        assert (
            p95_time < 200
        ), f"p95 response time {p95_time:.2f}ms exceeds 200ms"

    def test_concurrent_health_checks(self, client):
        """Should handle concurrent requests efficiently"""
        import concurrent.futures

        def make_request():
            start = time.perf_counter()
            response = client.get("/health")
            end = time.perf_counter()
            return (response.status_code, (end - start) * 1000)

        # Simulate 20 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(100)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        status_codes = [r[0] for r in results]
        assert all(code == 200 for code in status_codes), "Some requests failed"

        # Check performance
        times = [r[1] for r in results]
        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]

        print(
            f"\nConcurrent requests - Avg: {avg_time:.2f}ms, p95: {p95_time:.2f}ms"
        )

        # Should still be fast under concurrent load
        assert (
            avg_time < 100
        ), f"Average response time {avg_time:.2f}ms exceeds 100ms"
        assert (
            p95_time < 200
        ), f"p95 response time {p95_time:.2f}ms exceeds 200ms"


class TestMemoryUsage:
    """Test memory usage characteristics"""

    @pytest.mark.skip(reason="psutil not installed - optional performance metric")
    def test_no_memory_leak_on_repeated_requests(self):
        """Memory usage should remain stable across many requests"""
        import gc

        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not installed")

        process = psutil.Process()

        # Warm up
        client = TestClient(app)
        for _ in range(10):
            client.get("/health")

        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Make many requests
        for _ in range(1000):
            client.get("/health")

        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_increase = final_memory - initial_memory

        print(
            f"\nMemory: Initial={initial_memory:.2f}MB, "
            f"Final={final_memory:.2f}MB, "
            f"Increase={memory_increase:.2f}MB"
        )

        # Memory increase should be minimal (< 50MB for 1000 requests)
        assert (
            memory_increase < 50
        ), f"Memory increased by {memory_increase:.2f}MB"
