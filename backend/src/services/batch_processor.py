"""
分批處理服務 (Batch Processor Service)

負責協調 Facebook/Instagram 爬蟲執行,追蹤進度,並支援取消操作。
實現 FR-008 (進度追蹤) 與 FR-009 (取消爬取) 功能需求。

Author: COM_PAR Team
Date: 2025-11-14
"""

import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field

from ..models.post import Post
from ..models.comment import Comment
from .facebook_scraper import FacebookScraper, FacebookAuthRequired
from .instagram_scraper import InstagramScraper, InstagramAuthRequired


class ScrapeStatus(str, Enum):
    """爬取任務狀態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScrapeJob:
    """爬取任務資料結構"""
    id: str
    url: str
    platform: str
    status: ScrapeStatus = ScrapeStatus.PENDING
    progress: float = 0.0
    total_comments: int = 0
    scraped_comments: int = 0
    post_data: Optional[Post] = None
    comments: list[Comment] = field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancel_requested: bool = False


class BatchProcessorError(Exception):
    """批次處理器錯誤"""
    pass


class BatchProcessor:
    """
    批次處理器服務
    
    功能:
    - 建立並管理爬取任務
    - 協調 Facebook/Instagram 爬蟲執行
    - 追蹤爬取進度
    - 支援取消操作
    
    使用範例:
        processor = BatchProcessor()
        job_id = await processor.create_job("https://facebook.com/post/123")
        await processor.start_job(job_id)
        status = processor.get_job_status(job_id)
    """
    
    def __init__(
        self,
        facebook_scraper: Optional[FacebookScraper] = None,
        instagram_scraper: Optional[InstagramScraper] = None
    ):
        """
        初始化批次處理器
        
        Args:
            facebook_scraper: Facebook 爬蟲實例 (可選,用於測試注入)
            instagram_scraper: Instagram 爬蟲實例 (可選,用於測試注入)
        """
        self._jobs: Dict[str, ScrapeJob] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._facebook_scraper = facebook_scraper or FacebookScraper()
        self._instagram_scraper = instagram_scraper or InstagramScraper()
    
    def create_job(self, url: str, platform: str) -> str:
        """
        建立新的爬取任務
        
        Args:
            url: 貼文網址
            platform: 平台名稱 ('facebook' 或 'instagram')
        
        Returns:
            job_id: 任務唯一識別碼
        
        Raises:
            BatchProcessorError: 當平台不支援時
        """
        if platform not in ["facebook", "instagram"]:
            raise BatchProcessorError(f"Unsupported platform: {platform}")
        
        job_id = str(uuid.uuid4())
        job = ScrapeJob(
            id=job_id,
            url=url,
            platform=platform
        )
        self._jobs[job_id] = job
        return job_id
    
    async def start_job(self, job_id: str) -> None:
        """
        啟動爬取任務 (非阻塞)
        
        Args:
            job_id: 任務識別碼
        
        Raises:
            BatchProcessorError: 當任務不存在或已在執行中
        """
        if job_id not in self._jobs:
            raise BatchProcessorError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        
        if job.status == ScrapeStatus.RUNNING:
            raise BatchProcessorError(f"Job already running: {job_id}")
        
        # 建立非同步任務
        task = asyncio.create_task(self._execute_job(job_id))
        self._tasks[job_id] = task
    
    async def _execute_job(self, job_id: str) -> None:
        """
        執行爬取任務 (內部方法)
        
        Args:
            job_id: 任務識別碼
        """
        job = self._jobs[job_id]
        job.status = ScrapeStatus.RUNNING
        job.started_at = datetime.now()
        
        try:
            # 選擇對應的爬蟲
            scraper = (
                self._facebook_scraper if job.platform == "facebook"
                else self._instagram_scraper
            )
            
            # 爬取貼文資料
            job.post_data = await scraper.scrape_post(job.url)
            job.progress = 0.5  # 貼文資料完成 50%
            
            # 檢查取消請求
            if job.cancel_requested:
                job.status = ScrapeStatus.CANCELLED
                job.completed_at = datetime.now()
                return
            
            # 爬取留言資料 (帶進度回調)
            def progress_callback(current: int, total: int):
                if job.cancel_requested:
                    raise asyncio.CancelledError("Job cancelled by user")
                job.scraped_comments = current
                job.total_comments = total
                # 留言進度佔 50%-100%
                job.progress = 0.5 + (current / total * 0.5) if total > 0 else 1.0
            
            job.comments = await scraper.scrape_comments(
                job.url,
                progress_callback=progress_callback
            )
            
            # 更新最終計數
            job.total_comments = len(job.comments)
            job.scraped_comments = job.total_comments
            job.progress = 1.0
            job.status = ScrapeStatus.COMPLETED
            job.completed_at = datetime.now()
            
        except asyncio.CancelledError:
            job.status = ScrapeStatus.CANCELLED
            job.completed_at = datetime.now()
            job.error = "Job cancelled by user"
        
        except (FacebookAuthRequired, InstagramAuthRequired) as e:
            job.status = ScrapeStatus.FAILED
            job.completed_at = datetime.now()
            job.error = f"Authentication required: {str(e)}"
        
        except Exception as e:
            job.status = ScrapeStatus.FAILED
            job.completed_at = datetime.now()
            job.error = str(e)
        
        finally:
            # 清理任務引用
            if job_id in self._tasks:
                del self._tasks[job_id]
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        查詢任務狀態
        
        Args:
            job_id: 任務識別碼
        
        Returns:
            包含狀態、進度、留言數等資訊的字典
        
        Raises:
            BatchProcessorError: 當任務不存在時
        """
        if job_id not in self._jobs:
            raise BatchProcessorError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        return {
            "id": job.id,
            "url": job.url,
            "platform": job.platform,
            "status": job.status.value,
            "progress": job.progress,
            "total_comments": job.total_comments,
            "scraped_comments": job.scraped_comments,
            "error": job.error,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }
    
    def get_job_result(self, job_id: str) -> tuple[Optional[Post], list[Comment]]:
        """
        取得任務結果
        
        Args:
            job_id: 任務識別碼
        
        Returns:
            (post_data, comments) 元組
        
        Raises:
            BatchProcessorError: 當任務不存在或未完成時
        """
        if job_id not in self._jobs:
            raise BatchProcessorError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        
        if job.status != ScrapeStatus.COMPLETED:
            raise BatchProcessorError(
                f"Job not completed yet. Current status: {job.status.value}"
            )
        
        return job.post_data, job.comments
    
    def cancel_job(self, job_id: str) -> bool:
        """
        取消爬取任務
        
        Args:
            job_id: 任務識別碼
        
        Returns:
            是否成功請求取消 (True: 已請求取消, False: 任務已結束無法取消)
        
        Raises:
            BatchProcessorError: 當任務不存在時
        """
        if job_id not in self._jobs:
            raise BatchProcessorError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        
        # 已結束的任務無法取消
        if job.status in [ScrapeStatus.COMPLETED, ScrapeStatus.FAILED, ScrapeStatus.CANCELLED]:
            return False
        
        # 標記取消請求
        job.cancel_requested = True
        
        # 如果任務正在執行中,嘗試取消
        if job_id in self._tasks:
            task = self._tasks[job_id]
            task.cancel()
        
        # 如果任務還在 PENDING 狀態,直接標記為 CANCELLED
        if job.status == ScrapeStatus.PENDING:
            job.status = ScrapeStatus.CANCELLED
            job.completed_at = datetime.now()
            job.error = "Cancelled before execution"
        
        return True
    
    def list_jobs(self, status: Optional[ScrapeStatus] = None) -> list[Dict[str, Any]]:
        """
        列出所有任務
        
        Args:
            status: 篩選狀態 (可選)
        
        Returns:
            任務狀態列表
        """
        jobs = self._jobs.values()
        
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        return [self.get_job_status(job.id) for job in jobs]
    
    def cleanup_job(self, job_id: str) -> None:
        """
        清理已完成的任務
        
        Args:
            job_id: 任務識別碼
        
        Raises:
            BatchProcessorError: 當任務不存在或仍在執行中
        """
        if job_id not in self._jobs:
            raise BatchProcessorError(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        
        if job.status == ScrapeStatus.RUNNING:
            raise BatchProcessorError(f"Cannot cleanup running job: {job_id}")
        
        del self._jobs[job_id]
        
        if job_id in self._tasks:
            del self._tasks[job_id]
