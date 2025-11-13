"""
Contract tests for POST /api/scrape endpoint

These tests define the expected behavior of the scrape API endpoint
before implementation (TDD approach).
"""
import pytest
from fastapi.testclient import TestClient

from main import app


class TestScrapeContract:
    """Contract tests for scraping endpoint"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client"""
        return TestClient(app)

    def test_scrape_endpoint_exists(self, client: TestClient) -> None:
        """Test that POST /api/scrape endpoint is accessible"""
        response = client.post("/api/scrape", json={"url": "test"})
        # Should not return 404
        assert response.status_code != 404

    def test_scrape_requires_url(self, client: TestClient) -> None:
        """Test that URL is required in request body"""
        response = client.post("/api/scrape", json={})
        assert response.status_code == 400
        data = response.json()
        assert "url" in data.get("message", "").lower() or "url" in data.get(
            "error", ""
        ).lower()

    def test_scrape_validates_url_format(self, client: TestClient) -> None:
        """Test that invalid URL format is rejected"""
        response = client.post("/api/scrape", json={"url": "not-a-valid-url"})
        assert response.status_code == 400
        data = response.json()
        assert "url" in data.get("message", "").lower() or "invalid" in data.get(
            "message", ""
        ).lower()

    def test_scrape_validates_platform(self, client: TestClient) -> None:
        """Test that only supported platforms are accepted"""
        response = client.post(
            "/api/scrape", json={"url": "https://twitter.com/user/status/123"}
        )
        assert response.status_code == 400
        data = response.json()
        assert (
            "platform" in data.get("message", "").lower()
            or "supported" in data.get("message", "").lower()
        )

    def test_scrape_accepts_facebook_url(self, client: TestClient) -> None:
        """Test that valid Facebook URL is accepted"""
        response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        # Should accept request and return 201 or 202
        assert response.status_code in [201, 202]
        data = response.json()
        assert "scrape_id" in data
        assert "status" in data

    def test_scrape_accepts_instagram_url(self, client: TestClient) -> None:
        """Test that valid Instagram URL is accepted"""
        response = client.post(
            "/api/scrape",
            json={"url": "https://www.instagram.com/p/ABC123xyz/"},
        )
        # Should accept request and return 201 or 202
        assert response.status_code in [201, 202]
        data = response.json()
        assert "scrape_id" in data
        assert "status" in data

    def test_scrape_returns_scrape_id(self, client: TestClient) -> None:
        """Test that response includes scrape_id for tracking"""
        response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        assert response.status_code in [201, 202]
        data = response.json()
        assert "scrape_id" in data
        assert isinstance(data["scrape_id"], str)
        assert len(data["scrape_id"]) > 0

    def test_scrape_returns_initial_status(self, client: TestClient) -> None:
        """Test that response includes initial status"""
        response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        assert response.status_code in [201, 202]
        data = response.json()
        assert "status" in data
        # Status should be 'pending' or 'scraping'
        assert data["status"] in ["pending", "scraping", "queued"]

    def test_scrape_response_schema(self, client: TestClient) -> None:
        """Test that response follows expected schema"""
        response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        assert response.status_code in [201, 202]
        data = response.json()

        # Required fields
        assert "scrape_id" in data
        assert "status" in data
        assert "post_url" in data

        # Optional fields
        # message field may or may not be present

    def test_scrape_handles_duplicate_requests(self, client: TestClient) -> None:
        """Test that duplicate scrape requests are handled appropriately"""
        url = "https://www.facebook.com/test/posts/999999"

        # First request
        response1 = client.post("/api/scrape", json={"url": url})
        assert response1.status_code in [201, 202]
        scrape_id1 = response1.json()["scrape_id"]

        # Second request with same URL
        response2 = client.post("/api/scrape", json={"url": url})
        assert response2.status_code in [201, 202]
        scrape_id2 = response2.json()["scrape_id"]

        # Should either:
        # 1. Return the same scrape_id (de-duplication)
        # 2. Return a new scrape_id (allow multiple scrapes)
        # Both behaviors are acceptable
        assert isinstance(scrape_id2, str)

    def test_scrape_content_type(self, client: TestClient) -> None:
        """Test that endpoint requires JSON content type"""
        response = client.post(
            "/api/scrape",
            data="url=https://facebook.com/test/posts/123",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # Should reject non-JSON content or handle it appropriately
        assert response.status_code in [400, 415, 422]
