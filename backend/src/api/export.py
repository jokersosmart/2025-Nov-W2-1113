"""
匯出 API 端點 (Export API Endpoints)

實作以下端點:
- POST /api/export: 匯出貼文與留言資料為 Excel 檔案

符合 FR-012, FR-013, FR-026, FR-027 功能需求

Author: COM_PAR Team
Date: 2025-11-16
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ValidationError
from typing import List

from ..models.post import Post, Platform
from ..models.comment import Comment
from ..services.excel_generator import ExcelGenerator, ExcelGeneratorError

# 建立路由器
router = APIRouter(prefix="/api", tags=["export"])

# Excel 生成器實例
excel_generator = ExcelGenerator()


# ===== Request/Response Models =====


class ExportRequest(BaseModel):
    """匯出請求模型"""

    post: Post = Field(..., description="Post data to export")
    comments: List[Comment] = Field(..., description="List of comments to export")

    model_config = {
        "json_schema_extra": {
            "example": {
                "post": {
                    "platform": "facebook",
                    "post_url": "https://www.facebook.com/example/posts/123456789",
                    "post_time": "2025-11-16T14:30:00Z",
                    "post_content": "這是測試貼文內容",
                    "likes_count": 150,
                    "comments_count": 3,
                },
                "comments": [
                    {
                        "comment_id": "550e8400-e29b-41d4-a716-446655440001",
                        "post_url": "https://www.facebook.com/example/posts/123456789",
                        "comment_time": "2025-11-16T15:00:00Z",
                        "commenter_id": "王小明 (12345678)",
                        "comment_content": "很棒的分享!",
                        "reply_window": "張專員",
                        "reply_content": "感謝您的支持!",
                        "customer_notes": "已確認",
                        "generated_reply": "",
                    }
                ],
            }
        }
    }


# ===== API Endpoints =====


@router.post(
    "/export",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Export post and comments to Excel",
    description="Generate and download an Excel file (.xlsx) containing post and comments data",
    responses={
        200: {
            "description": "Excel file generated successfully",
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {
                    "schema": {"type": "string", "format": "binary"}
                }
            },
        },
        400: {
            "description": "Invalid request data",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation error",
                        "message": "post field is required",
                    }
                }
            },
        },
        500: {
            "description": "Excel generation failed",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Export error",
                        "message": "Failed to generate Excel file",
                    }
                }
            },
        },
    },
)
async def export_to_excel(request: ExportRequest) -> StreamingResponse:
    """
    匯出為 Excel 檔案 (FR-012, FR-013)

    接收貼文與留言資料,生成包含 12 個欄位的 Excel 檔案:
    - 發文時間、貼文連結、貼文內容、按讚數、留言總數
    - 留言時間、留言者 ID、留言內容
    - 回覆窗口、回覆內容、客戶確認、生成回覆

    Args:
        request: 包含 post 與 comments 的匯出請求

    Returns:
        StreamingResponse: Excel 檔案 (.xlsx)

    Raises:
        HTTPException 400: 請求資料驗證失敗
        HTTPException 500: Excel 生成過程錯誤
    """
    # 驗證請求資料
    if request.post is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Validation error", "message": "post field is required"},
        )

    if request.comments is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation error",
                "message": "comments field is required",
            },
        )

    # 驗證平台
    if request.post.platform not in [Platform.FACEBOOK, Platform.INSTAGRAM]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation error",
                "message": f"Unsupported platform: {request.post.platform}. Only facebook and instagram are supported.",
            },
        )

    try:
        # 生成 Excel 檔案
        excel_file = excel_generator.generate(request.post, request.comments)

        # 生成檔名 (FR-026, FR-027)
        filename = ExcelGenerator.generate_filename(request.post.platform.value)

        # 返回檔案
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache",
            },
        )

    except ExcelGeneratorError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Export error", "message": str(e)},
        ) from e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Export error",
                "message": f"Failed to generate Excel file: {str(e)}",
            },
        ) from e
