"""
批次處理器服務單元測試

測試涵蓋:
- 任務建立與管理
- 爬取執行流程
- 進度追蹤
- 取消操作
- 錯誤處理

Author: COM_PAR Team
Date: 2025-11-14
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

from src.services.batch_processor import (
    BatchProcessor,
    ScrapeJob,
    ScrapeStatus,
    BatchProcessorError
)
from src.models.post import Post
from src.models.comment import Comment


@pytest.fixture
def mock_facebook_scraper():
    """模擬 Facebook 爬蟲"""
    scraper = AsyncMock()
    scraper.scrape_post = AsyncMock(return_value=Post(
        platform="facebook",
        post_url="https://facebook.com/post/123",
        post_time=datetime.now(),
        post_content="Test post",
        likes_count=100,
        comments_count=5
    ))
    scraper.scrape_comments = AsyncMock(return_value=[
        Comment(
            comment_id="550e8400-e29b-41d4-a716-446655440001",
            post_url="https://facebook.com/post/123",
            comment_time=datetime.now(),
            comment_content="Comment 1",
            commenter_id="User1 (12345)"
        ),
        Comment(
            comment_id="550e8400-e29b-41d4-a716-446655440002",
            post_url="https://facebook.com/post/123",
            comment_time=datetime.now(),
            comment_content="Comment 2",
            commenter_id="User2 (67890)"
        )
    ])
    return scraper


@pytest.fixture
def mock_instagram_scraper():
    """模擬 Instagram 爬蟲"""
    scraper = AsyncMock()
    scraper.scrape_post = AsyncMock(return_value=Post(
        platform="instagram",
        post_url="https://instagram.com/p/ABC123",
        post_time=datetime.now(),
        post_content="Test post",
        likes_count=200,
        comments_count=3
    ))
    scraper.scrape_comments = AsyncMock(return_value=[
        Comment(
            comment_id="550e8400-e29b-41d4-a716-446655440003",
            post_url="https://instagram.com/p/ABC123",
            comment_time=datetime.now(),
            comment_content="Nice!",
            commenter_id="user1 (99999)"
        )
    ])
    return scraper


@pytest.fixture
def processor(mock_facebook_scraper, mock_instagram_scraper):
    """建立批次處理器實例"""
    return BatchProcessor(
        facebook_scraper=mock_facebook_scraper,
        instagram_scraper=mock_instagram_scraper
    )


class TestBatchProcessorCreation:
    """測試任務建立"""
    
    def test_create_facebook_job(self, processor):
        """測試建立 Facebook 任務"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        assert job_id is not None
        assert isinstance(job_id, str)
        assert len(job_id) == 36  # UUID 格式
        
        status = processor.get_job_status(job_id)
        assert status["platform"] == "facebook"
        assert status["status"] == "pending"
        assert status["progress"] == 0.0
    
    def test_create_instagram_job(self, processor):
        """測試建立 Instagram 任務"""
        job_id = processor.create_job(
            "https://instagram.com/p/ABC123",
            "instagram"
        )
        
        status = processor.get_job_status(job_id)
        assert status["platform"] == "instagram"
        assert status["status"] == "pending"
    
    def test_create_job_unsupported_platform(self, processor):
        """測試不支援的平台"""
        with pytest.raises(BatchProcessorError, match="Unsupported platform"):
            processor.create_job("https://twitter.com/post/123", "twitter")
    
    def test_get_nonexistent_job(self, processor):
        """測試查詢不存在的任務"""
        with pytest.raises(BatchProcessorError, match="Job not found"):
            processor.get_job_status("nonexistent-id")


class TestBatchProcessorExecution:
    """測試任務執行"""
    
    @pytest.mark.asyncio
    async def test_execute_facebook_job(self, processor, mock_facebook_scraper):
        """測試執行 Facebook 爬取任務"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        await processor.start_job(job_id)
        
        # 等待任務完成
        await asyncio.sleep(0.1)
        
        status = processor.get_job_status(job_id)
        assert status["status"] == "completed"
        assert status["progress"] == 1.0
        assert status["total_comments"] == 2
        
        # 驗證爬蟲被呼叫
        mock_facebook_scraper.scrape_post.assert_called_once()
        mock_facebook_scraper.scrape_comments.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_instagram_job(self, processor, mock_instagram_scraper):
        """測試執行 Instagram 爬取任務"""
        job_id = processor.create_job(
            "https://instagram.com/p/ABC123",
            "instagram"
        )
        
        await processor.start_job(job_id)
        await asyncio.sleep(0.1)
        
        status = processor.get_job_status(job_id)
        assert status["status"] == "completed"
        assert status["total_comments"] == 1
        
        mock_instagram_scraper.scrape_post.assert_called_once()
        mock_instagram_scraper.scrape_comments.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_already_running_job(self, processor, mock_facebook_scraper):
        """測試重複啟動任務"""
        # 讓爬蟲執行較長時間以確保任務保持 RUNNING 狀態
        async def slow_scrape(*args, **kwargs):
            await asyncio.sleep(0.5)
            return []
        
        mock_facebook_scraper.scrape_comments.side_effect = slow_scrape
        
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        await processor.start_job(job_id)
        
        # 等待任務狀態變為 RUNNING
        await asyncio.sleep(0.1)
        
        # 嘗試再次啟動應該失敗
        with pytest.raises(BatchProcessorError, match="already running"):
            await processor.start_job(job_id)
    
    @pytest.mark.asyncio
    async def test_get_job_result(self, processor):
        """測試取得任務結果"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        await processor.start_job(job_id)
        await asyncio.sleep(0.1)
        
        post, comments = processor.get_job_result(job_id)
        
        assert post is not None
        assert post.platform.value == "facebook"
        assert len(comments) == 2
        assert "User1" in comments[0].commenter_id
    
    @pytest.mark.asyncio
    async def test_get_result_before_completion(self, processor):
        """測試在完成前取得結果"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        with pytest.raises(BatchProcessorError, match="not completed"):
            processor.get_job_result(job_id)


class TestBatchProcessorCancellation:
    """測試取消操作"""
    
    def test_cancel_pending_job(self, processor):
        """測試取消等待中的任務"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        result = processor.cancel_job(job_id)
        
        assert result is True
        status = processor.get_job_status(job_id)
        assert status["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_cancel_running_job(self, processor, mock_facebook_scraper):
        """測試取消執行中的任務"""
        # 讓爬蟲執行時間較長
        async def slow_scrape(*args, **kwargs):
            await asyncio.sleep(1)
            return []
        
        mock_facebook_scraper.scrape_comments = slow_scrape
        
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        await processor.start_job(job_id)
        await asyncio.sleep(0.1)  # 讓任務開始執行
        
        result = processor.cancel_job(job_id)
        
        assert result is True
        await asyncio.sleep(0.2)  # 等待取消完成
        
        status = processor.get_job_status(job_id)
        assert status["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_cancel_completed_job(self, processor):
        """測試取消已完成的任務"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        await processor.start_job(job_id)
        await asyncio.sleep(0.1)
        
        result = processor.cancel_job(job_id)
        
        assert result is False  # 無法取消已完成的任務


class TestBatchProcessorErrorHandling:
    """測試錯誤處理"""
    
    @pytest.mark.asyncio
    async def test_scraper_exception(self, processor, mock_facebook_scraper):
        """測試爬蟲拋出異常"""
        mock_facebook_scraper.scrape_post.side_effect = Exception("Network error")
        
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        await processor.start_job(job_id)
        await asyncio.sleep(0.1)
        
        status = processor.get_job_status(job_id)
        assert status["status"] == "failed"
        assert "Network error" in status["error"]


class TestBatchProcessorManagement:
    """測試任務管理"""
    
    def test_list_all_jobs(self, processor):
        """測試列出所有任務"""
        job1 = processor.create_job("https://facebook.com/post/1", "facebook")
        job2 = processor.create_job("https://instagram.com/p/1", "instagram")
        
        jobs = processor.list_jobs()
        
        assert len(jobs) == 2
        assert any(j["id"] == job1 for j in jobs)
        assert any(j["id"] == job2 for j in jobs)
    
    @pytest.mark.asyncio
    async def test_list_jobs_by_status(self, processor):
        """測試按狀態篩選任務"""
        job1 = processor.create_job("https://facebook.com/post/1", "facebook")
        job2 = processor.create_job("https://facebook.com/post/2", "facebook")
        
        await processor.start_job(job1)
        await asyncio.sleep(0.1)
        
        completed_jobs = processor.list_jobs(status=ScrapeStatus.COMPLETED)
        pending_jobs = processor.list_jobs(status=ScrapeStatus.PENDING)
        
        assert len(completed_jobs) == 1
        assert len(pending_jobs) == 1
    
    @pytest.mark.asyncio
    async def test_cleanup_job(self, processor):
        """測試清理任務"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        await processor.start_job(job_id)
        await asyncio.sleep(0.1)
        
        processor.cleanup_job(job_id)
        
        with pytest.raises(BatchProcessorError, match="Job not found"):
            processor.get_job_status(job_id)
    
    def test_cleanup_running_job(self, processor):
        """測試清理執行中的任務"""
        job_id = processor.create_job(
            "https://facebook.com/post/123",
            "facebook"
        )
        
        # 不啟動,直接清理 PENDING 任務
        processor.cleanup_job(job_id)  # 應該成功
