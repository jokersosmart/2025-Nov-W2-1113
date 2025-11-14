"""
爬取 API 端點 (Scrape API Endpoints)

實作以下端點:
- POST /api/scrape: 啟動爬取任務
- GET /api/scrape/{id}/progress: 查詢爬取進度
- POST /api/scrape/{id}/cancel: 取消爬取任務

符合 FR-006, FR-008, FR-009, FR-014 功能需求

Author: COM_PAR Team
Date: 2025-11-14
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from typing import Literal

from ..services.batch_processor import BatchProcessor, BatchProcessorError, ScrapeStatus
from ..utils.url_validator import URLValidator

# 建立路由器
router = APIRouter(prefix="/api", tags=["scraping"])

# 全域批次處理器實例
batch_processor = BatchProcessor()

# URL 驗證器
url_validator = URLValidator()


# ===== Request/Response Models =====


class ScrapeRequest(BaseModel):
    """爬取請求模型"""
    url: HttpUrl = Field(..., description="Facebook or Instagram post URL")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://www.facebook.com/example/posts/123456789"
            }
        }
    }


class ScrapeResponse(BaseModel):
    """爬取響應模型"""
    scrape_id: str = Field(..., description="Unique scrape job identifier")
    status: Literal["pending", "running", "completed", "failed", "cancelled"] = Field(
        ..., description="Current job status"
    )
    message: str = Field(..., description="Status message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "scrape_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
                "message": "Scrape job created successfully"
            }
        }
    }


class ProgressResponse(BaseModel):
    """進度響應模型"""
    scrape_id: str = Field(..., description="Scrape job identifier")
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage (0.0-1.0)")
    total_comments: int = Field(..., ge=0, description="Total comments found")
    scraped_comments: int = Field(..., ge=0, description="Comments scraped so far")
    error: str | None = Field(None, description="Error message if failed")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "scrape_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "running",
                "progress": 0.65,
                "total_comments": 100,
                "scraped_comments": 65,
                "error": None
            }
        }
    }


class CancelResponse(BaseModel):
    """取消響應模型"""
    scrape_id: str
    status: Literal["pending", "running", "completed", "failed", "cancelled"]
    message: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "scrape_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "cancelled",
                "message": "Scrape job cancelled successfully"
            }
        }
    }


# ===== API Endpoints =====


@router.post(
    "/scrape",
    response_model=ScrapeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start scraping a post",
    description="Create and start a scraping job for a Facebook or Instagram post URL",
)
async def create_scrape_job(request: ScrapeRequest) -> ScrapeResponse:
    """
    啟動爬取任務 (FR-006)
    
    Args:
        request: 包含貼文 URL 的請求
    
    Returns:
        ScrapeResponse: 包含 scrape_id 和狀態的響應
    
    Raises:
        HTTPException 400: URL 格式無效或平台不支援
        HTTPException 403: 需要登入驗證的私人貼文
        HTTPException 500: 伺服器內部錯誤
    """
    url_str = str(request.url)
    
    try:
        # FR-014: 驗證 URL 格式
        validation = url_validator.validate_url(url_str)
        
        if not validation.is_valid:
            # 檢查是否需要登入
            if validation.status == "requires_auth":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Authentication required",
                        "message": validation.message,
                        "url": url_str
                    }
                )
            
            # 其他驗證錯誤 (格式無效、未知平台等)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid URL",
                    "message": validation.message,
                    "url": url_str
                }
            )
        
        platform = validation.platform
        
        # 建立爬取任務
        scrape_id = batch_processor.create_job(url_str, platform)
        
        # 啟動任務 (非阻塞)
        await batch_processor.start_job(scrape_id)
        
        return ScrapeResponse(
            scrape_id=scrape_id,
            status="pending",
            message="Scrape job created successfully"
        )
    
    except BatchProcessorError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to create scrape job",
                "message": str(e)
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )


@router.get(
    "/scrape/{scrape_id}/progress",
    response_model=ProgressResponse,
    summary="Get scraping progress",
    description="Query the progress of a scraping job by its ID",
)
async def get_scrape_progress(scrape_id: str) -> ProgressResponse:
    """
    查詢爬取進度 (FR-008)
    
    Args:
        scrape_id: 爬取任務識別碼
    
    Returns:
        ProgressResponse: 包含進度、狀態、留言數的響應
    
    Raises:
        HTTPException 404: 任務不存在
        HTTPException 500: 伺服器內部錯誤
    """
    try:
        job_status = batch_processor.get_job_status(scrape_id)
        
        return ProgressResponse(
            scrape_id=scrape_id,
            status=job_status["status"],
            progress=job_status["progress"],
            total_comments=job_status["total_comments"],
            scraped_comments=job_status["scraped_comments"],
            error=job_status["error"]
        )
    
    except BatchProcessorError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Job not found",
                "message": f"Scrape job with ID {scrape_id} does not exist",
                "scrape_id": scrape_id
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )


@router.post(
    "/scrape/{scrape_id}/cancel",
    response_model=CancelResponse,
    summary="Cancel a scraping job",
    description="Cancel an ongoing scraping job. Idempotent operation.",
)
async def cancel_scrape_job(scrape_id: str) -> CancelResponse:
    """
    取消爬取任務 (FR-009)
    
    Args:
        scrape_id: 爬取任務識別碼
    
    Returns:
        CancelResponse: 包含取消狀態的響應
    
    Raises:
        HTTPException 404: 任務不存在
        HTTPException 500: 伺服器內部錯誤
    
    Note:
        此操作為冪等性 - 多次取消同一任務不會產生錯誤
    """
    try:
        # 嘗試取消任務
        cancelled = batch_processor.cancel_job(scrape_id)
        
        # 取得最新狀態
        job_status = batch_processor.get_job_status(scrape_id)
        current_status = job_status["status"]
        
        if cancelled:
            message = "Scrape job cancelled successfully"
        else:
            # 任務已結束,無法取消
            if current_status == "completed":
                message = "Job already completed, cannot cancel"
            elif current_status == "failed":
                message = "Job already failed, cannot cancel"
            elif current_status == "cancelled":
                message = "Job already cancelled"
            else:
                message = "Job cannot be cancelled in current state"
        
        return CancelResponse(
            scrape_id=scrape_id,
            status=current_status,
            message=message
        )
    
    except BatchProcessorError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Job not found",
                "message": f"Scrape job with ID {scrape_id} does not exist",
                "scrape_id": scrape_id
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": str(e)
            }
        )
