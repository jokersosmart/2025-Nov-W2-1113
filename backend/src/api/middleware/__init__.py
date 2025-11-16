"""
API middleware package
"""
from src.api.middleware.error_handler import (
    AppError,
    InvalidURLError,
    NetworkError,
    RateLimitError,
    ScraperError,
    add_error_handlers,
)

__all__ = [
    "AppError",
    "InvalidURLError",
    "NetworkError",
    "RateLimitError",
    "ScraperError",
    "add_error_handlers",
]
