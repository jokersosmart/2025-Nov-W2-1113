"""
Unit tests for Post model
"""
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.models.post import Platform, Post


class TestPostModel:
    """Test suite for Post model"""

    def test_create_valid_facebook_post(self):
        """Test creating a valid Facebook post"""
        post = Post(
            platform=Platform.FACEBOOK,
            post_url="https://www.facebook.com/example/posts/123456789",
            post_time=datetime(2025, 11, 13, 14, 30, 52, tzinfo=UTC),
            post_content="這是一則範例貼文內容",
            likes_count=128,
            comments_count=45,
        )

        assert post.platform == Platform.FACEBOOK
        assert "facebook.com" in str(post.post_url)
        assert post.likes_count == 128
        assert post.comments_count == 45

    def test_create_valid_instagram_post(self):
        """Test creating a valid Instagram post"""
        post = Post(
            platform=Platform.INSTAGRAM,
            post_url="https://www.instagram.com/p/ABC123/",
            post_time=datetime(2025, 11, 13, 14, 30, 52, tzinfo=UTC),
            post_content="IG post content",
            likes_count=256,
            comments_count=89,
        )

        assert post.platform == Platform.INSTAGRAM
        assert "instagram.com" in str(post.post_url)

    def test_negative_likes_count_raises_error(self):
        """Test that negative likes count raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            Post(
                platform=Platform.FACEBOOK,
                post_url="https://www.facebook.com/example/posts/123",
                post_time=datetime.now(UTC),
                post_content="Test",
                likes_count=-1,
                comments_count=0,
            )

        assert "likes_count" in str(exc_info.value)

    def test_negative_comments_count_raises_error(self):
        """Test that negative comments count raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            Post(
                platform=Platform.FACEBOOK,
                post_url="https://www.facebook.com/example/posts/123",
                post_time=datetime.now(UTC),
                post_content="Test",
                likes_count=0,
                comments_count=-1,
            )

        assert "comments_count" in str(exc_info.value)

    def test_post_content_max_length(self):
        """Test post content maximum length validation"""
        long_content = "x" * 10001  # Exceeds max length of 10000

        with pytest.raises(ValidationError) as exc_info:
            Post(
                platform=Platform.FACEBOOK,
                post_url="https://www.facebook.com/example/posts/123",
                post_time=datetime.now(UTC),
                post_content=long_content,
                likes_count=0,
                comments_count=0,
            )

        assert "post_content" in str(exc_info.value)

    def test_platform_url_mismatch_raises_error(self):
        """Test that platform and URL must match"""
        with pytest.raises(ValidationError) as exc_info:
            Post(
                platform=Platform.FACEBOOK,
                post_url="https://www.instagram.com/p/ABC123/",  # Mismatch!
                post_time=datetime.now(UTC),
                post_content="Test",
                likes_count=0,
                comments_count=0,
            )

        assert "facebook.com" in str(exc_info.value)

    def test_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            Post()

    def test_model_json_schema(self):
        """Test model has correct JSON schema example"""
        schema = Post.model_json_schema()
        assert "example" in schema
        assert schema["example"]["platform"] == "facebook"
