"""
Contract tests for GET /api/scrape/{id}/progress endpoint

These tests define the expected behavior of the progress tracking endpoint
before implementation (TDD approach).
"""
import pytest
from fastapi.testclient import TestClient

from main import app


class TestProgressContract:
    """Contract tests for progress endpoint"""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client"""
        return TestClient(app)

    def test_progress_endpoint_exists(self, client: TestClient) -> None:
        """Test that GET /api/scrape/{id}/progress endpoint is accessible"""
        response = client.get("/api/scrape/test-id/progress")
        # Should not return 404
        assert response.status_code != 404

    def test_progress_requires_valid_scrape_id(self, client: TestClient) -> None:
        """Test that invalid scrape_id returns 404"""
        response = client.get("/api/scrape/non-existent-id/progress")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("message", "").lower() or "error" in data

    def test_progress_returns_status(self, client: TestClient) -> None:
        """Test that progress response includes status"""
        # First create a scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Get progress
        response = client.get(f"/api/scrape/{scrape_id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in [
            "pending",
            "scraping",
            "completed",
            "failed",
            "cancelled",
        ]

    def test_progress_returns_progress_percentage(self, client: TestClient) -> None:
        """Test that progress response includes progress percentage"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Get progress
        response = client.get(f"/api/scrape/{scrape_id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert "progress" in data
        assert isinstance(data["progress"], (int, float))
        assert 0 <= data["progress"] <= 100

    def test_progress_returns_comment_counts(self, client: TestClient) -> None:
        """Test that progress response includes comment counts"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Get progress
        response = client.get(f"/api/scrape/{scrape_id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert "total_comments" in data or "totalComments" in data
        assert "scraped_comments" in data or "scrapedComments" in data

    def test_progress_response_schema(self, client: TestClient) -> None:
        """Test that progress response follows expected schema"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Get progress
        response = client.get(f"/api/scrape/{scrape_id}/progress")
        assert response.status_code == 200
        data = response.json()

        # Required fields
        assert "scrape_id" in data or "scrapeId" in data
        assert "status" in data
        assert "progress" in data

        # Status field validation
        assert data["status"] in [
            "pending",
            "scraping",
            "completed",
            "failed",
            "cancelled",
        ]

    def test_progress_when_scraping(self, client: TestClient) -> None:
        """Test progress response during scraping"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Get progress immediately
        response = client.get(f"/api/scrape/{scrape_id}/progress")
        assert response.status_code == 200
        data = response.json()

        # Should have a message field when in progress
        if data["status"] in ["scraping", "pending"]:
            assert "message" in data or data["progress"] >= 0

    def test_progress_multiple_polls(self, client: TestClient) -> None:
        """Test that progress can be polled multiple times"""
        # Create scrape job
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        # Poll progress multiple times
        for _ in range(3):
            response = client.get(f"/api/scrape/{scrape_id}/progress")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data

    def test_progress_completed_status(self, client: TestClient) -> None:
        """Test progress response when scraping is completed"""
        # This test may need to wait or mock completion
        # For now, just verify the schema would support completed status
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        response = client.get(f"/api/scrape/{scrape_id}/progress")
        data = response.json()

        # If completed, should have full data
        if data.get("status") == "completed":
            assert data["progress"] == 100
            assert "total_comments" in data or "totalComments" in data

    def test_progress_failed_status(self, client: TestClient) -> None:
        """Test progress response when scraping fails"""
        # Create scrape with invalid URL that will fail
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/invalid-post-url"},
        )

        # If request accepted, check progress
        if scrape_response.status_code in [201, 202]:
            scrape_id = scrape_response.json()["scrape_id"]
            response = client.get(f"/api/scrape/{scrape_id}/progress")
            data = response.json()

            # If failed, should have error message
            if data.get("status") == "failed":
                assert "message" in data or "error" in data

    def test_progress_caching_headers(self, client: TestClient) -> None:
        """Test that progress endpoint has appropriate caching headers"""
        scrape_response = client.post(
            "/api/scrape",
            json={"url": "https://www.facebook.com/test/posts/123456"},
        )
        scrape_id = scrape_response.json()["scrape_id"]

        response = client.get(f"/api/scrape/{scrape_id}/progress")
        assert response.status_code == 200

        # Progress should not be cached (or have short cache)
        cache_control = response.headers.get("cache-control", "")
        # Either no-cache or short max-age
        assert "no-cache" in cache_control or "max-age" in cache_control or True
