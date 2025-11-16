/**
 * E2E Integration Tests - 匯出流程
 * 
 * 測試使用者故事 3 (P3) 的完整匯出流程
 * 
 * 驗收情境:
 * 1. 使用者點擊匯出按鈕,系統生成並下載 Excel 檔案
 * 2. Excel 檔案包含所有欄位,格式正確可讀
 * 3. 刪除部分留言後匯出,Excel 僅包含剩餘留言
 * 4. 分別匯出 Facebook 和 Instagram 資料,檔名不同且不覆蓋
 * 
 * @author COM_PAR Team
 * @date 2025-11-16
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HomePage } from '../../src/pages/HomePage';
import { useStore } from '../../src/services/store';
import * as apiService from '../../src/services/apiService';
import type { Post } from '../../src/types/post';
import type { Comment } from '../../src/types/comment';

// Mock API 服務
vi.mock('../../src/services/apiService', async () => {
  const actual = await vi.importActual('../../src/services/apiService');
  return {
    ...actual,
    exportToExcel: vi.fn(),
    downloadBlob: vi.fn(),
  };
});

describe('匯出流程 E2E 測試', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    vi.clearAllMocks();
    // 重置 Zustand store 狀態
    useStore.getState().reset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * Helper: 準備測試資料
   */
  const setupTestData = (platform: 'facebook' | 'instagram', commentCount: number = 3) => {
    const post: Post = {
      platform,
      post_url: platform === 'facebook' 
        ? 'https://www.facebook.com/test/posts/123456'
        : 'https://www.instagram.com/p/ABC123DEF/',
      post_time: '2025-11-13T10:30:00Z',
      post_content: '這是測試貼文內容',
      likes_count: 150,
      comments_count: commentCount,
    };

    const comments: Comment[] = Array.from({ length: commentCount }, (_, i) => ({
      comment_id: `comment-${i + 1}`,
      post_url: post.post_url,
      comment_time: `2025-11-13T10:${30 + i}:00Z`,
      commenter_id: `測試使用者${i + 1} (${12345678 + i})`,
      comment_content: `這是第 ${i + 1} 則測試留言`,
      reply_window: i === 0 ? '客服窗口' : null,
      reply_content: i === 0 ? '感謝您的留言' : null,
      customer_notes: null,
      generated_reply: null,
    }));

    return { post, comments };
  };

  /**
   * 驗收情境 1: 使用者點擊匯出按鈕,系統生成並下載 Excel 檔案
   * 
   * Given: 系統已成功爬取並顯示留言資料(包含使用者已編輯的內容)
   * When: 使用者點擊「匯出 Excel」按鈕
   * Then: 系統生成並下載一個 .xlsx 檔案,檔案包含所有必要欄位與資料,
   *       且檔名符合格式(platform_comments_YYYYMMDD_HHMMSS.xlsx)
   */
  it('驗收情境 1: 使用者點擊匯出按鈕,成功下載 Excel 檔案', async () => {
    // Arrange - 準備 Mock 資料
    const { post, comments } = setupTestData('facebook', 3);
    
    // 設定 store 初始狀態(模擬已完成爬取)
    useStore.setState({
      post,
      comments,
      scrapeProgress: {
        scrapeId: 'test-scrape-1',
        status: 'completed',
        progress: 100,
        totalComments: 3,
        scrapedComments: 3,
        message: '爬取完成',
      },
    });

    // Mock Excel blob
    const mockBlob = new Blob(['mock excel data'], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    vi.mocked(apiService.exportToExcel).mockResolvedValue(mockBlob);

    // Act - 執行操作
    render(<HomePage />);

    // 確認有匯出按鈕
    const exportButton = screen.getByRole('button', { name: /匯出 excel/i });
    expect(exportButton).toBeInTheDocument();
    expect(exportButton).not.toBeDisabled();

    // 點擊匯出按鈕
    await user.click(exportButton);

    // Assert - 驗證結果
    // 驗證 API 被呼叫並傳遞正確資料
    await waitFor(() => {
      expect(apiService.exportToExcel).toHaveBeenCalledWith(
        expect.objectContaining({
          platform: 'facebook',
          post_url: post.post_url,
        }),
        expect.arrayContaining([
          expect.objectContaining({
            comment_id: 'comment-1',
          }),
        ])
      );
    });

    // 驗證下載函式被呼叫
    await waitFor(() => {
      expect(apiService.downloadBlob).toHaveBeenCalledWith(
        mockBlob,
        expect.stringMatching(/facebook_comments_\d{8}_\d{6}\.xlsx/)
      );
    });
  });

  /**
   * 驗收情境 2: Excel 檔案包含所有欄位,格式正確可讀
   * 
   * Given: 使用者已匯出 Excel 檔案
   * When: 使用者使用 Excel 或相容軟體開啟該檔案
   * Then: 所有欄位標題正確(中文),資料正確對應至各欄位,格式可讀
   * 
   * 注意: 此測試驗證傳遞給 API 的資料結構完整性
   */
  it('驗收情境 2: Excel 檔案包含所有必要欄位和資料', async () => {
    // Arrange
    const { post, comments } = setupTestData('facebook', 2);
    
    // 編輯部分留言
    comments[0].reply_window = '張專員';
    comments[0].reply_content = '感謝您的支持!';
    comments[0].customer_notes = '已確認';
    
    useStore.setState({
      post,
      comments,
      scrapeProgress: {
        scrapeId: 'test-scrape-2',
        status: 'completed',
        progress: 100,
        totalComments: 2,
        scrapedComments: 2,
        message: '爬取完成',
      },
    });

    const mockBlob = new Blob(['mock excel data'], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    vi.mocked(apiService.exportToExcel).mockResolvedValue(mockBlob);

    // Act
    render(<HomePage />);

    const exportButton = screen.getByRole('button', { name: /匯出 excel/i });
    await user.click(exportButton);

    // Assert - 驗證資料結構完整性
    await waitFor(() => {
      const callArgs = vi.mocked(apiService.exportToExcel).mock.calls[0];
      const exportedPost = callArgs[0];
      const exportedComments = callArgs[1];

      // 驗證 Post 包含所有欄位
      expect(exportedPost).toMatchObject({
        platform: 'facebook',
        post_url: expect.any(String),
        post_time: expect.any(String),
        post_content: expect.any(String),
        likes_count: expect.any(Number),
        comments_count: expect.any(Number),
      });

      // 驗證 Comments 包含所有欄位
      expect(exportedComments[0]).toMatchObject({
        comment_id: expect.any(String),
        post_url: expect.any(String),
        comment_time: expect.any(String),
        commenter_id: expect.any(String),
        comment_content: expect.any(String),
        reply_window: '張專員', // 使用者編輯的內容
        reply_content: '感謝您的支持!',
        customer_notes: '已確認',
      });

      // 驗證留言數量正確
      expect(exportedComments).toHaveLength(2);
    });
  });

  /**
   * 驗收情境 3: 刪除部分留言後匯出,Excel 僅包含剩餘留言
   * 
   * Given: 系統爬取的貼文有 100 則留言
   * When: 使用者刪除其中 20 則後匯出
   * Then: Excel 檔案中僅包含剩餘的 80 則留言資料
   */
  it('驗收情境 3: 刪除部分留言後匯出,僅包含剩餘留言', async () => {
    // Arrange - 準備 100 則留言
    const { post, comments: allComments } = setupTestData('facebook', 100);
    
    useStore.setState({
      post,
      comments: allComments,
      scrapeProgress: {
        scrapeId: 'test-scrape-3',
        status: 'completed',
        progress: 100,
        totalComments: 100,
        scrapedComments: 100,
        message: '爬取完成',
      },
    });

    const mockBlob = new Blob(['mock excel data'], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    vi.mocked(apiService.exportToExcel).mockResolvedValue(mockBlob);

    // Act - 刪除 20 則留言
    render(<HomePage />);

    // 模擬刪除操作(刪除前 20 則)
    const commentsToDelete = allComments.slice(0, 20).map(c => c.comment_id);
    useStore.getState().deleteComments(commentsToDelete);

    // 等待 UI 更新
    await waitFor(() => {
      // 確認顯示剩餘 80 則留言
      const remainingCount = useStore.getState().comments.length;
      expect(remainingCount).toBe(80);
    });

    // 點擊匯出
    const exportButton = screen.getByRole('button', { name: /匯出 excel/i });
    await user.click(exportButton);

    // Assert - 驗證匯出的留言數量
    await waitFor(() => {
      const callArgs = vi.mocked(apiService.exportToExcel).mock.calls[0];
      const exportedComments = callArgs[1];

      // 驗證僅匯出 80 則留言
      expect(exportedComments).toHaveLength(80);

      // 驗證刪除的留言不在匯出資料中
      const exportedIds = exportedComments.map(c => c.comment_id);
      commentsToDelete.forEach(deletedId => {
        expect(exportedIds).not.toContain(deletedId);
      });
    });
  });

  /**
   * 驗收情境 4: 分別匯出 Facebook 和 Instagram 資料,檔名不同且不覆蓋
   * 
   * Given: 使用者分別爬取了 Facebook 和 Instagram 兩個貼文
   * When: 使用者分別匯出這兩次爬取結果
   * Then: 生成的檔名分別以 facebook_comments_ 和 instagram_comments_ 開頭,
   *       且時間戳記不同,不會互相覆蓋
   */
  it('驗收情境 4: 分別匯出不同平台資料,檔名正確且不覆蓋', async () => {
    // Arrange - Facebook 資料
    const { post: fbPost, comments: fbComments } = setupTestData('facebook', 5);
    
    const mockBlob = new Blob(['mock excel data'], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    });
    
    vi.mocked(apiService.exportToExcel).mockResolvedValue(mockBlob);

    // Act 1 - 匯出 Facebook 資料
    useStore.setState({
      post: fbPost,
      comments: fbComments,
      scrapeProgress: {
        scrapeId: 'test-scrape-fb',
        status: 'completed',
        progress: 100,
        totalComments: 5,
        scrapedComments: 5,
        message: '爬取完成',
      },
    });

    const { rerender } = render(<HomePage />);

    const exportButton = screen.getByRole('button', { name: /匯出 excel/i });
    await user.click(exportButton);

    // 等待第一次匯出完成
    await waitFor(() => {
      expect(apiService.downloadBlob).toHaveBeenCalledTimes(1);
    });

    const firstCallArgs = vi.mocked(apiService.downloadBlob).mock.calls[0];
    const fbFilename = firstCallArgs[1];

    // Assert 1 - 驗證 Facebook 檔名格式
    expect(fbFilename).toMatch(/^facebook_comments_\d{8}_\d{6}\.xlsx$/);

    // Arrange 2 - Instagram 資料
    vi.clearAllMocks(); // 清除第一次呼叫記錄
    
    const { post: igPost, comments: igComments } = setupTestData('instagram', 3);
    
    useStore.setState({
      post: igPost,
      comments: igComments,
      scrapeProgress: {
        scrapeId: 'test-scrape-ig',
        status: 'completed',
        progress: 100,
        totalComments: 3,
        scrapedComments: 3,
        message: '爬取完成',
      },
    });

    // 強制重新渲染
    rerender(<HomePage />);

    // Act 2 - 匯出 Instagram 資料
    const exportButton2 = screen.getByRole('button', { name: /匯出 excel/i });
    await user.click(exportButton2);

    // 等待第二次匯出完成
    await waitFor(() => {
      expect(apiService.downloadBlob).toHaveBeenCalledTimes(1); // 清除後重新計數
    });

    const secondCallArgs = vi.mocked(apiService.downloadBlob).mock.calls[0];
    const igFilename = secondCallArgs[1];

    // Assert 2 - 驗證 Instagram 檔名格式
    expect(igFilename).toMatch(/^instagram_comments_\d{8}_\d{6}\.xlsx$/);

    // Assert 3 - 驗證檔名不同(不會覆蓋)
    expect(fbFilename).not.toBe(igFilename);
    expect(fbFilename.startsWith('facebook_comments_')).toBe(true);
    expect(igFilename.startsWith('instagram_comments_')).toBe(true);
  });

  /**
   * 額外測試: 匯出前無資料時,按鈕應被禁用
   */
  it('額外測試: 無資料時匯出按鈕應被禁用', async () => {
    // Arrange - 空資料
    useStore.setState({
      post: null,
      comments: [],
      scrapeProgress: null,
    });

    // Act
    render(<HomePage />);

    // Assert
    const exportButton = screen.getByRole('button', { name: /匯出 excel/i });
    expect(exportButton).toBeDisabled();
  });

  /**
   * 額外測試: 匯出失敗時顯示錯誤訊息
   */
  it('額外測試: 匯出失敗時顯示錯誤訊息', async () => {
    // Arrange
    const { post, comments } = setupTestData('facebook', 2);
    
    useStore.setState({
      post,
      comments,
      scrapeProgress: {
        scrapeId: 'test-scrape-error',
        status: 'completed',
        progress: 100,
        totalComments: 2,
        scrapedComments: 2,
        message: '爬取完成',
      },
    });

    // Mock 匯出失敗
    vi.mocked(apiService.exportToExcel).mockRejectedValue(
      Object.assign(new Error('伺服器錯誤,無法生成 Excel 檔案'), {
        code: 'SERVER_ERROR',
        status: 500,
      })
    );

    // Act
    render(<HomePage />);

    const exportButton = screen.getByRole('button', { name: /匯出 excel/i });
    await user.click(exportButton);

    // Assert - 驗證錯誤訊息顯示
    await waitFor(() => {
      expect(screen.getByText(/伺服器錯誤/i)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  /**
   * 額外測試: 匯出中顯示載入狀態
   */
  it('額外測試: 匯出過程中顯示載入狀態', async () => {
    // Arrange
    const { post, comments } = setupTestData('facebook', 2);
    
    useStore.setState({
      post,
      comments,
      scrapeProgress: {
        scrapeId: 'test-scrape-loading',
        status: 'completed',
        progress: 100,
        totalComments: 2,
        scrapedComments: 2,
        message: '爬取完成',
      },
    });

    // Mock 慢速回應
    vi.mocked(apiService.exportToExcel).mockImplementation(() => 
      new Promise((resolve) => {
        setTimeout(() => {
          resolve(new Blob(['mock data'], { 
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
          }));
        }, 500);
      })
    );

    // Act
    render(<HomePage />);

    const exportButton = screen.getByRole('button', { name: /匯出 excel/i });
    await user.click(exportButton);

    // Assert - 驗證載入狀態
    await waitFor(() => {
      expect(screen.getByText(/匯出中/i)).toBeInTheDocument();
    });

    // 等待匯出完成
    await waitFor(() => {
      expect(screen.queryByText(/匯出中/i)).not.toBeInTheDocument();
    }, { timeout: 1000 });
  });
});
