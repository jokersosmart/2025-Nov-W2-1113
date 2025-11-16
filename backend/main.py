"""
FastAPI application entry point for Social Comment Scraper
"""
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware import add_error_handlers

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

# Register unified error handlers
add_error_handlers(app)


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
