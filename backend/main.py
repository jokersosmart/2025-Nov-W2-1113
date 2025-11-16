"""
FastAPI application entry point for Social Comment Scraper
"""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Application metadata
APP_VERSION = "0.1.0"
APP_TITLE = "Social Comment Scraper API"
APP_DESCRIPTION = """
API for scraping comments from social media platforms (Facebook, Instagram).

Features:
- Scrape public post comments
- Real-time progress tracking
- Export to Excel
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"Starting {APP_TITLE} v{APP_VERSION}")
    yield
    # Shutdown
    print(f"Shutting down {APP_TITLE}")


# Create FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default dev server
        "http://localhost:3000",  # Alternative dev port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handling middleware
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """將 Pydantic 驗證錯誤統一返回 400 而非 422"""
    errors = exc.errors()
    # 提取第一個錯誤資訊
    first_error = errors[0] if errors else {}
    field_name = first_error.get("loc", ["unknown"])[-1]
    error_type = first_error.get("type", "validation_error")

    # 根據錯誤類型生成友善訊息
    if "missing" in error_type:
        message = f"{field_name} is required"
    else:
        message = str(first_error.get("msg", "Invalid request data"))

    # 清理 error details,移除不可序列化的物件
    cleaned_errors = []
    for error in errors:
        cleaned_error = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        # 只在 input 可序列化時才加入
        input_value = error.get("input")
        if input_value is not None and not isinstance(input_value, bytes):
            cleaned_error["input"] = input_value
        cleaned_errors.append(cleaned_error)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "message": message,
            "details": cleaned_errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url),
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handler for validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Validation error",
            "message": str(exc),
            "path": str(request.url),
        },
    )


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "service": APP_TITLE,
    }


# Root endpoint
@app.get("/", tags=["System"])
async def root() -> dict[str, str]:
    """
    Root endpoint with API information

    Returns:
        dict: Welcome message and documentation link
    """
    return {
        "message": f"Welcome to {APP_TITLE}",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# API routes
from src.api import scrape, export

app.include_router(scrape.router)
app.include_router(export.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
