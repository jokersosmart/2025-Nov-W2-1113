"""
Unit tests for Comment model
"""
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.models.comment import Comment


class TestCommentModel:
    """Test suite for Comment Pydantic model"""

    def test_create_valid_comment(self) -> None:
        """Test creating a valid comment with all required fields"""
        comment = Comment(
            comment_id=str(uuid4()),
            post_url="https://www.facebook.com/example/posts/123456789",
            comment_time=datetime.now(timezone.utc),
            commenter_id="John Doe (12345678)",
            comment_content="This is a great post!",
        )
        assert comment.comment_id is not None
        assert "facebook.com" in str(comment.post_url)
        assert comment.comment_time is not None
        assert comment.commenter_id == "John Doe (12345678)"
        assert comment.comment_content == "This is a great post!"
        assert comment.reply_window is None
        assert comment.reply_content is None
        assert comment.customer_notes is None
        assert comment.generated_reply is None

    def test_create_comment_with_optional_fields(self) -> None:
        """Test creating a comment with optional edit fields"""
        comment = Comment(
            comment_id=str(uuid4()),
            post_url="https://www.instagram.com/p/ABC123/",
            comment_time=datetime.now(timezone.utc),
            commenter_id="@jane_doe (87654321)",
            comment_content="Nice picture!",
            reply_window="Customer Service A",
            reply_content="Thank you for your comment!",
            customer_notes="VIP customer",
            generated_reply="",
        )
        assert comment.reply_window == "Customer Service A"
        assert comment.reply_content == "Thank you for your comment!"
        assert comment.customer_notes == "VIP customer"
        assert comment.generated_reply == ""

    def test_comment_content_max_length(self) -> None:
        """Test that comment_content enforces max length of 5000 characters"""
        with pytest.raises(ValidationError) as exc_info:
            Comment(
                comment_id=str(uuid4()),
                post_url="https://www.facebook.com/example/posts/123",
                comment_time=datetime.now(timezone.utc),
                commenter_id="Test User (111)",
                comment_content="x" * 5001,  # Exceeds 5000 char limit
            )
        errors = exc_info.value.errors()
        assert any("comment_content" in str(error["loc"]) for error in errors)

    def test_reply_window_max_length(self) -> None:
        """Test that reply_window enforces max length of 100 characters"""
        with pytest.raises(ValidationError) as exc_info:
            Comment(
                comment_id=str(uuid4()),
                post_url="https://www.facebook.com/example/posts/123",
                comment_time=datetime.now(timezone.utc),
                commenter_id="Test User (111)",
                comment_content="Test content",
                reply_window="x" * 101,  # Exceeds 100 char limit
            )
        errors = exc_info.value.errors()
        assert any("reply_window" in str(error["loc"]) for error in errors)

    def test_reply_content_max_length(self) -> None:
        """Test that reply_content enforces max length of 1000 characters"""
        with pytest.raises(ValidationError) as exc_info:
            Comment(
                comment_id=str(uuid4()),
                post_url="https://www.facebook.com/example/posts/123",
                comment_time=datetime.now(timezone.utc),
                commenter_id="Test User (111)",
                comment_content="Test content",
                reply_content="x" * 1001,  # Exceeds 1000 char limit
            )
        errors = exc_info.value.errors()
        assert any("reply_content" in str(error["loc"]) for error in errors)

    def test_customer_notes_max_length(self) -> None:
        """Test that customer_notes enforces max length of 500 characters"""
        with pytest.raises(ValidationError) as exc_info:
            Comment(
                comment_id=str(uuid4()),
                post_url="https://www.facebook.com/example/posts/123",
                comment_time=datetime.now(timezone.utc),
                commenter_id="Test User (111)",
                comment_content="Test content",
                customer_notes="x" * 501,  # Exceeds 500 char limit
            )
        errors = exc_info.value.errors()
        assert any("customer_notes" in str(error["loc"]) for error in errors)

    def test_generated_reply_max_length(self) -> None:
        """Test that generated_reply enforces max length of 1000 characters"""
        with pytest.raises(ValidationError) as exc_info:
            Comment(
                comment_id=str(uuid4()),
                post_url="https://www.facebook.com/example/posts/123",
                comment_time=datetime.now(timezone.utc),
                commenter_id="Test User (111)",
                comment_content="Test content",
                generated_reply="x" * 1001,  # Exceeds 1000 char limit
            )
        errors = exc_info.value.errors()
        assert any("generated_reply" in str(error["loc"]) for error in errors)

    def test_missing_required_fields(self) -> None:
        """Test that creating comment without required fields raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Comment()  # Missing all required fields
        errors = exc_info.value.errors()
        required_fields = {
            "comment_id",
            "post_url",
            "comment_time",
            "commenter_id",
            "comment_content",
        }
        error_fields = {error["loc"][0] for error in errors}
        assert required_fields.issubset(error_fields)

    def test_invalid_uuid_format(self) -> None:
        """Test that invalid UUID format for comment_id raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            Comment(
                comment_id="not-a-valid-uuid",
                post_url="https://www.facebook.com/example/posts/123",
                comment_time=datetime.now(timezone.utc),
                commenter_id="Test User (111)",
                comment_content="Test content",
            )
        errors = exc_info.value.errors()
        assert any("comment_id" in str(error["loc"]) for error in errors)

    def test_model_json_schema(self) -> None:
        """Test that model can generate JSON schema with example"""
        schema = Comment.model_json_schema()
        assert "properties" in schema
        assert "comment_id" in schema["properties"]
        assert "post_url" in schema["properties"]
        assert "comment_content" in schema["properties"]
