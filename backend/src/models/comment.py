"""
Comment entity model
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Comment(BaseModel):
    """
    Comment model representing a first-level comment on a social media post

    Attributes:
        comment_id: Unique identifier (UUID v4)
        post_url: URL of the parent post
        comment_time: Timestamp when comment was posted
        commenter_id: Commenter identification (format: "Name (ID)")
        comment_content: Text content of the comment (max 5000 chars)
        reply_window: Reply window name (user-editable, max 100 chars)
        reply_content: Reply content text (user-editable, max 1000 chars)
        customer_notes: Customer notes/modifications (user-editable, max 500 chars)
        generated_reply: AI-generated reply placeholder (future feature, max 1000 chars)
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "comment_id": "550e8400-e29b-41d4-a716-446655440000",
                "post_url": "https://www.facebook.com/example/posts/123456789",
                "comment_time": "2025-11-13T14:35:20+08:00",
                "commenter_id": "張小明 (87654321)",
                "comment_content": "這個產品很棒!想了解更多資訊。",
                "reply_window": "客服 A",
                "reply_content": "感謝您的詢問,我們會盡快與您聯繫。",
                "customer_notes": "高優先客戶",
                "generated_reply": "",
            }
        }
    )

    comment_id: str | UUID = Field(
        ...,
        description="Unique identifier for the comment (UUID v4)",
    )
    post_url: HttpUrl = Field(
        ...,
        description="URL of the parent post (foreign key)",
    )
    comment_time: datetime = Field(
        ...,
        description="Timestamp when the comment was posted",
    )
    commenter_id: str = Field(
        ...,
        min_length=1,
        description='Commenter identification in format "Name (ID)"',
    )
    comment_content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text content of the comment",
    )
    reply_window: str | None = Field(
        default=None,
        max_length=100,
        description="Reply window name (user-editable)",
    )
    reply_content: str | None = Field(
        default=None,
        max_length=1000,
        description="Reply content text (user-editable)",
    )
    customer_notes: str | None = Field(
        default=None,
        max_length=500,
        description="Customer notes/modifications (user-editable)",
    )
    generated_reply: str | None = Field(
        default=None,
        max_length=1000,
        description="AI-generated reply placeholder (future feature)",
    )

    @field_validator("comment_id")
    @classmethod
    def validate_uuid_format(cls, v: str | UUID) -> str | UUID:
        """Validate that comment_id is a valid UUID format"""
        if isinstance(v, str):
            try:
                UUID(v)
            except ValueError as e:
                raise ValueError("comment_id must be a valid UUID format") from e
        return v

    @field_validator("reply_window", "reply_content", "customer_notes", "generated_reply")
    @classmethod
    def allow_empty_strings(cls, v: str | None) -> str | None:
        """Allow empty strings for user-editable fields (user can clear content)"""
        if v == "":
            return v
        return v
