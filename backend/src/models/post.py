"""
Post model - represents a social media post (Facebook or Instagram)
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Platform(str, Enum):
    """Supported social media platforms"""

    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class Post(BaseModel):
    """
    A public post from Facebook or Instagram

    Attributes:
        platform: Source platform (facebook or instagram)
        post_url: Original post URL (FR-007)
        post_time: Post creation timestamp (FR-003)
        post_content: Post text content (FR-003)
        likes_count: Number of likes (FR-003)
        comments_count: Total number of comments (FR-003)
    """

    platform: Platform = Field(..., description="Source platform (facebook or instagram)")
    post_url: HttpUrl = Field(..., description="Original post URL")
    post_time: datetime = Field(..., description="Post creation timestamp (ISO 8601)")
    post_content: str = Field(..., max_length=10000, description="Post text content")
    likes_count: int = Field(..., ge=0, description="Number of likes")
    comments_count: int = Field(..., ge=0, description="Total number of comments")

    @field_validator("post_url")
    @classmethod
    def validate_post_url(cls, v: HttpUrl, info) -> HttpUrl:
        """Validate URL matches the specified platform"""
        url_str = str(v)
        platform = info.data.get("platform")

        if platform == Platform.FACEBOOK and "facebook.com" not in url_str:
            raise ValueError("Facebook post URL must contain 'facebook.com'")
        if platform == Platform.INSTAGRAM and "instagram.com" not in url_str:
            raise ValueError("Instagram post URL must contain 'instagram.com'")

        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "platform": "facebook",
                "post_url": "https://www.facebook.com/example/posts/123456789",
                "post_time": "2025-11-13T14:30:52+08:00",
                "post_content": "這是一則範例貼文內容",
                "likes_count": 128,
                "comments_count": 45,
            }
        }
    }
