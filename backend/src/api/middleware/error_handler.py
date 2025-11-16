"""
Unified error handling middleware for FastAPI application

Provides consistent error responses across all endpoints and handles:
- Custom application errors (AppError)
- Domain-specific errors (InvalidURLError, NetworkError, etc.)
- FastAPI HTTPException
- Request validation errors (Pydantic)
- Unhandled exceptions

All error responses follow a consistent format:
{
    "error": "Error Type",
    "message": "User-friendly message",
    "timestamp": "ISO 8601 timestamp",
    "path": "/request/path",
    "details": {} (optional)
}
"""
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# Custom exception classes
class AppError(Exception):
    """Base application error with custom status code"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class InvalidURLError(AppError):
    """Raised when URL format is invalid or post is inaccessible"""

    def __init__(self, url: str, details: str | None = None):
        message = f"無法存取此貼文,請確認網址是否正確且為公開貼文: {url}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"url": url, "reason": details} if details else {"url": url},
        )


class NetworkError(AppError):
    """Raised when network connection fails"""

    def __init__(self, message: str = "網路連線失敗,請檢查網路設定"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RateLimitError(AppError):
    """Raised when platform rate limit is detected"""

    def __init__(
        self, message: str = "平台偵測到頻繁存取,請稍後再試", retry_after: int = 60
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after},
        )
        self.retry_after = retry_after


class ScraperError(AppError):
    """Raised when scraper encounters an error"""

    def __init__(self, message: str, technical_details: str | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"technical_details": technical_details} if technical_details else {},
        )


# Error response formatter
def create_error_response(
    error_type: str,
    message: str,
    status_code: int,
    request: Request,
    details: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """
    Create standardized error response

    Args:
        error_type: Error classification (e.g., "Validation Error")
        message: User-friendly error message
        status_code: HTTP status code
        request: FastAPI request object
        details: Optional additional error details
        headers: Optional HTTP headers

    Returns:
        JSONResponse with standardized error format
    """
    response_data = {
        "error": error_type,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": str(request.url.path),
    }

    if details:
        response_data["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=response_data,
        headers=headers or {},
    )


# Exception handlers
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle custom AppError exceptions"""
    return create_error_response(
        error_type=exc.__class__.__name__.replace("Error", " Error").replace("  ", " ").strip(),
        message=exc.message,
        status_code=exc.status_code,
        request=request,
        details=exc.details if exc.details else None,
    )


async def invalid_url_error_handler(request: Request, exc: InvalidURLError) -> JSONResponse:
    """Handle InvalidURLError exceptions"""
    return create_error_response(
        error_type="Invalid URL",
        message=exc.message,
        status_code=exc.status_code,
        request=request,
        details=exc.details,
    )


async def network_error_handler(request: Request, exc: NetworkError) -> JSONResponse:
    """Handle NetworkError exceptions"""
    return create_error_response(
        error_type="Network Error",
        message=exc.message,
        status_code=exc.status_code,
        request=request,
    )


async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:
    """Handle RateLimitError exceptions with Retry-After header"""
    headers = {"Retry-After": str(exc.retry_after)}

    return create_error_response(
        error_type="Rate Limit Exceeded",
        message=exc.message,
        status_code=exc.status_code,
        request=request,
        details={"retry_after": exc.retry_after},
        headers=headers,
    )


async def scraper_error_handler(request: Request, exc: ScraperError) -> JSONResponse:
    """Handle ScraperError exceptions"""
    return create_error_response(
        error_type="Scraper Error",
        message=exc.message,
        status_code=exc.status_code,
        request=request,
        details=exc.details if exc.details else None,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPException"""
    # Map status code to error type
    error_types = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
    }

    error_type = error_types.get(exc.status_code, "Error")

    return create_error_response(
        error_type=error_type,
        message=str(exc.detail),
        status_code=exc.status_code,
        request=request,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = exc.errors()

    # Extract validation error details
    error_details = []
    for error in errors:
        # Get field path
        field_path = " -> ".join(str(loc) for loc in error.get("loc", []))

        error_detail = {
            "field": field_path,
            "message": error.get("msg", ""),
            "type": error.get("type", ""),
        }

        # Include input value if available and serializable
        input_value = error.get("input")
        if input_value is not None and not isinstance(input_value, (bytes, type)):
            try:
                # Try to convert to string representation
                error_detail["input"] = str(input_value)
            except Exception:
                pass

        error_details.append(error_detail)

    # Create user-friendly message from first error
    first_error = errors[0] if errors else {}
    field_name = first_error.get("loc", ["unknown"])[-1]
    error_msg = first_error.get("msg", "Invalid request data")

    if "missing" in first_error.get("type", ""):
        message = f"Required field missing: {field_name}"
    elif "invalid" in error_msg.lower():
        message = f"Invalid value for field: {field_name}"
    else:
        message = f"Validation error: {error_msg}"

    return create_error_response(
        error_type="Validation Error",
        message=message,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        request=request,
        details=error_details,
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions"""
    # Log the exception (in production, use proper logging)
    import traceback

    print(f"Unhandled exception: {exc}")
    print(traceback.format_exc())

    # In production, don't expose internal error details
    # For now, include the error message for debugging
    return create_error_response(
        error_type="Internal Server Error",
        message="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request=request,
        details={"error": str(exc)} if str(exc) else None,
    )


# Register all error handlers
def add_error_handlers(app: FastAPI) -> None:
    """
    Register all error handlers to the FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Custom application errors
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(InvalidURLError, invalid_url_error_handler)
    app.add_exception_handler(NetworkError, network_error_handler)
    app.add_exception_handler(RateLimitError, rate_limit_error_handler)
    app.add_exception_handler(ScraperError, scraper_error_handler)

    # FastAPI built-in exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)

    # Global exception handler (catch-all)
    app.add_exception_handler(Exception, global_exception_handler)
