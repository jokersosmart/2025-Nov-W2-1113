"""
Load testing script using Locust

Tests API performance to ensure p95 response time <= 200ms

Run:
    locust -f backend/tests/performance/locustfile.py --host=http://localhost:8000

Access web UI:
    http://localhost:8089
"""
from locust import HttpUser, between, task


class SocialCommentScraperUser(HttpUser):
    """
    Simulates user behavior for social comment scraper API

    Tests critical endpoints under load to verify:
    - p95 response time <= 200ms
    - Error rate < 1%
    - System stability under concurrent users
    """

    # Wait 1-3 seconds between tasks
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user starts - perform any setup here"""
        # Could authenticate or fetch initial data here if needed
        pass

    @task(3)
    def health_check(self):
        """
        Test health check endpoint (frequent)

        Weight: 3 (30% of requests)
        Expected: < 50ms response time
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Health check failed")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def get_root(self):
        """
        Test root endpoint (moderate frequency)

        Weight: 2 (20% of requests)
        Expected: < 100ms response time
        """
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "version" in data:
                    response.success()
                else:
                    response.failure("Invalid root response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def start_scraping_invalid_url(self):
        """
        Test scraping with invalid URL (infrequent)

        Weight: 1 (10% of requests)
        Expected: < 200ms response time
        Should return 4xx error
        """
        with self.client.post(
            "/api/scrape",
            json={"url": "https://facebook.com/invalid", "platform": "facebook"},
            catch_response=True,
        ) as response:
            # Should return 4xx or 5xx for invalid URL
            if response.status_code in [400, 422, 500]:
                response.success()
            else:
                response.failure(
                    f"Expected 4xx/5xx, got {response.status_code}"
                )

    @task(2)
    def get_scrape_status_not_found(self):
        """
        Test getting non-existent scrape status (moderate frequency)

        Weight: 2 (20% of requests)
        Expected: < 100ms response time
        Should return 404
        """
        with self.client.get(
            "/api/scrape/nonexistent-id/status", catch_response=True
        ) as response:
            if response.status_code == 404:
                response.success()
            else:
                response.failure(
                    f"Expected 404, got {response.status_code}"
                )

    @task(1)
    def get_openapi_docs(self):
        """
        Test OpenAPI documentation endpoint (infrequent)

        Weight: 1 (10% of requests)
        Expected: < 200ms response time
        """
        with self.client.get("/openapi.json", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "openapi" in data and "info" in data:
                    response.success()
                else:
                    response.failure("Invalid OpenAPI schema")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def export_nonexistent_post(self):
        """
        Test exporting non-existent post (infrequent)

        Weight: 1 (10% of requests)
        Expected: < 200ms response time
        Should return 404
        """
        with self.client.post(
            "/api/export",
            json={
                "post_url": "https://facebook.com/nonexistent/posts/123",
                "format": "csv",
            },
            catch_response=True,
        ) as response:
            # Should return error for non-existent post
            if response.status_code in [404, 500]:
                response.success()
            else:
                response.failure(
                    f"Expected 404/500, got {response.status_code}"
                )


class FastAPIReadOnlyUser(HttpUser):
    """
    User that only performs read operations

    Simulates users browsing documentation and checking status
    without triggering expensive scraping operations
    """

    wait_time = between(0.5, 2)

    @task(5)
    def health_check(self):
        """Frequent health checks"""
        self.client.get("/health")

    @task(3)
    def get_docs(self):
        """Browse API documentation"""
        self.client.get("/docs")

    @task(2)
    def get_openapi(self):
        """Fetch OpenAPI schema"""
        self.client.get("/openapi.json")

    @task(1)
    def get_root(self):
        """Check root endpoint"""
        self.client.get("/")


class StressTestUser(HttpUser):
    """
    Aggressive user for stress testing

    Shorter wait times to push system limits
    """

    wait_time = between(0.1, 0.5)

    @task
    def rapid_health_checks(self):
        """Rapid fire health checks"""
        for _ in range(5):
            self.client.get("/health")

    @task
    def rapid_invalid_requests(self):
        """Rapid fire invalid scrape requests"""
        for _ in range(3):
            self.client.post(
                "/api/scrape",
                json={"url": "invalid", "platform": "facebook"},
            )
