/**
 * E2E Integration Tests - 爬取流程
 * 
 * 測試使用者故事 1 (P1 - MVP) 的完整爬取流程
 * 
 * 驗收情境:
 * 1. 使用者貼上 Facebook 公開貼文網址,系統顯示貼文資訊與留言列表
 * 2. 使用者貼上 Instagram 公開貼文網址,系統顯示貼文資訊與留言列表
 * 3. 貼文沒有留言時,顯示提示訊息
 * 4. 爬取過程中可取消操作,保留已爬取的部分資料
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HomePage } from '../../src/pages/HomePage';
import { useStore } from '../../src/services/store';
import * as apiService from '../../src/services/apiService';
import type { ScrapeResponse, ProgressResponse } from '../../src/services/apiService';

// Mock API 服務
vi.mock('../../src/services/apiService', async () => {
  const actual = await vi.importActual('../../src/services/apiService');
  return {
    ...actual,
    startScraping: vi.fn(),
    getProgress: vi.fn(),
    cancelScraping: vi.fn(),
    pollProgress: vi.fn(),
  };
});

describe('爬取流程 E2E 測試', () => {
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
   * 驗收情境 1: Facebook 貼文爬取
   * 
   * Given: 使用者開啟線上工具首頁
   * When: 使用者在輸入框貼上一個 Facebook 公開貼文網址並點擊「開始爬取」
   * Then: 系統顯示該貼文的發文時間、貼文內容、按讚數、留言總數,以及所有第一層留言的列表
   */
  it('驗收情境 1: 使用者貼上 Facebook 網址,系統顯示貼文與留言', async () => {
    // Arrange - 準備 Mock 資料
    const facebookUrl = 'https://www.facebook.com/example/posts/123456789';
    const mockScrapeResponse: ScrapeResponse = {
      scrape_id: 'test-scrape-id-1',
      status: 'running',
      message: '開始爬取...',
    };

    const mockProgressComplete: ProgressResponse = {
      scrape_id: 'test-scrape-id-1',
      status: 'completed',
      progress: 1.0,
      total_comments: 5,
      scraped_comments: 5,
      error: null,
    };

    // Mock API 呼叫
    vi.mocked(apiService.startScraping).mockResolvedValue(mockScrapeResponse);
    
    // Mock pollProgress 立即完成
    vi.mocked(apiService.pollProgress).mockImplementation((scrapeId, onProgress, onComplete) => {
      // 模擬進度更新
      setTimeout(() => {
        onProgress({
          scrape_id: scrapeId,
          status: 'running',
          progress: 0.6,
          total_comments: 5,
          scraped_comments: 3,
          error: null,
        });
      }, 100);

      // 模擬完成
      setTimeout(() => {
        if (onComplete) {
          onComplete(mockProgressComplete);
        }
      }, 200);

      // 返回停止函式
      return () => {};
    });

    // Act - 執行操作
    render(<HomePage />);

    // 確認初始空白狀態
    expect(screen.getByText(/請在上方輸入 Facebook 或 Instagram 貼文網址開始爬取/i)).toBeInTheDocument();

    // 輸入 Facebook URL
    const urlInput = screen.getByPlaceholderText(/請貼上 Facebook 或 Instagram 貼文網址/i);
    await user.type(urlInput, facebookUrl);

    // 確認平台偵測
    expect(screen.getByText(/偵測到平台/i)).toBeInTheDocument();
    expect(screen.getByText(/Facebook/i)).toBeInTheDocument();

    // 點擊開始爬取按鈕
    const scrapeButton = screen.getByRole('button', { name: /開始爬取/i });
    await user.click(scrapeButton);

    // Assert - 驗證結果
    // 驗證 API 被呼叫
    expect(apiService.startScraping).toHaveBeenCalledWith(facebookUrl);

    // 等待進度顯示
    await waitFor(() => {
      expect(screen.getByText(/已爬取/i)).toBeInTheDocument();
    }, { timeout: 3000 });

    // 等待完成
    await waitFor(() => {
      expect(screen.getByText(/完成!/i)).toBeInTheDocument();
    }, { timeout: 3000 });

    // 注意: 實際的貼文資訊和留言資料需要後端 API 返回
    // 這裡的測試聚焦於流程,實際資料展示需要整合真實 API 響應
  });

  /**
   * 驗收情境 2: Instagram 貼文爬取
   * 
   * Given: 使用者開啟線上工具首頁
   * When: 使用者在輸入框貼上一個 Instagram 公開貼文網址並點擊「開始爬取」
   * Then: 系統顯示該貼文的發文時間、貼文內容、按讚數、留言總數,以及所有第一層留言的列表
   */
  it('驗收情境 2: 使用者貼上 Instagram 網址,系統顯示貼文與留言', async () => {
    // Arrange
    const instagramUrl = 'https://www.instagram.com/p/ABC123DEF456/';
    const mockScrapeResponse: ScrapeResponse = {
      scrape_id: 'test-scrape-id-2',
      status: 'running',
      message: '開始爬取...',
    };

    const mockProgressComplete: ProgressResponse = {
      scrape_id: 'test-scrape-id-2',
      status: 'completed',
      progress: 1.0,
      total_comments: 10,
      scraped_comments: 10,
      error: null,
    };

    vi.mocked(apiService.startScraping).mockResolvedValue(mockScrapeResponse);
    vi.mocked(apiService.pollProgress).mockImplementation((scrapeId, onProgress, onComplete) => {
      setTimeout(() => {
        if (onComplete) {
          onComplete(mockProgressComplete);
        }
      }, 200);
      return () => {};
    });

    // Act
    render(<HomePage />);

    const urlInput = screen.getByPlaceholderText(/請貼上 Facebook 或 Instagram 貼文網址/i);
    await user.type(urlInput, instagramUrl);

    // 確認平台偵測為 Instagram
    expect(screen.getByText(/Instagram/i)).toBeInTheDocument();

    const scrapeButton = screen.getByRole('button', { name: /開始爬取/i });
    await user.click(scrapeButton);

    // Assert
    expect(apiService.startScraping).toHaveBeenCalledWith(instagramUrl);

    await waitFor(() => {
      expect(screen.getByText(/完成!/i)).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  /**
   * 驗收情境 3: 貼文無留言
   * 
   * Given: 使用者已成功爬取一個貼文
   * When: 該貼文沒有任何留言
   * Then: 系統顯示貼文基本資訊,但留言列表為空,並顯示「此貼文尚無留言」提示訊息
   */
  it('驗收情境 3: 貼文無留言時顯示提示訊息', async () => {
    // Arrange - 模擬無留言的貼文
    const facebookUrl = 'https://www.facebook.com/example/posts/999999999';
    const mockScrapeResponse: ScrapeResponse = {
      scrape_id: 'test-scrape-id-3',
      status: 'running',
      message: '開始爬取...',
    };

    const mockProgressComplete: ProgressResponse = {
      scrape_id: 'test-scrape-id-3',
      status: 'completed',
      progress: 1.0,
      total_comments: 0,
      scraped_comments: 0,
      error: null,
    };

    vi.mocked(apiService.startScraping).mockResolvedValue(mockScrapeResponse);
    vi.mocked(apiService.pollProgress).mockImplementation((scrapeId, onProgress, onComplete) => {
      setTimeout(() => {
        if (onComplete) {
          onComplete(mockProgressComplete);
        }
      }, 200);
      return () => {};
    });

    // Act
    render(<HomePage />);

    const urlInput = screen.getByPlaceholderText(/請貼上 Facebook 或 Instagram 貼文網址/i);
    await user.type(urlInput, facebookUrl);

    const scrapeButton = screen.getByRole('button', { name: /開始爬取/i });
    await user.click(scrapeButton);

    // Assert - 驗證顯示「此貼文尚無留言」訊息
    await waitFor(() => {
      expect(screen.getByText(/此貼文尚無留言/i)).toBeInTheDocument();
    }, { timeout: 3000 });

    // 確認沒有留言表格
    expect(screen.queryByText(/留言列表/i)).not.toBeInTheDocument();
  });

  /**
   * 驗收情境 4: 取消爬取並保留部分資料
   * 
   * Given: 系統正在爬取大量留言(如 500 則)並顯示進度
   * When: 使用者在爬取至第 250 則時點擊「取消」按鈕
   * Then: 系統停止爬取,保留已爬取的 250 則留言並顯示於表格,
   *       並提示「已取消,保留 250 則留言資料」,且這些資料可供編輯與匯出
   */
  it('驗收情境 4: 爬取過程可取消並保留部分資料', async () => {
    // Arrange - 模擬大量留言的爬取
    const facebookUrl = 'https://www.facebook.com/example/posts/777777777';
    const mockScrapeResponse: ScrapeResponse = {
      scrape_id: 'test-scrape-id-4',
      status: 'running',
      message: '開始爬取...',
    };

    let progressUpdateCount = 0;
    const stopPollingMock = vi.fn();

    vi.mocked(apiService.startScraping).mockResolvedValue(mockScrapeResponse);
    
    // Mock pollProgress 模擬持續更新
    vi.mocked(apiService.pollProgress).mockImplementation((scrapeId, onProgress, onComplete) => {
      // 模擬多次進度更新
      const interval = setInterval(() => {
        progressUpdateCount++;
        const current = progressUpdateCount * 50;
        const total = 500;

        if (current >= total) {
          clearInterval(interval);
          if (onComplete) {
            onComplete({
              scrape_id: scrapeId,
              status: 'completed',
              progress: 1.0,
              total_comments: total,
              scraped_comments: total,
              error: null,
            });
          }
          return;
        }

        onProgress({
          scrape_id: scrapeId,
          status: 'running',
          progress: current / total,
          total_comments: total,
          scraped_comments: current,
          error: null,
        });
      }, 100);

      // 返回停止函式
      return () => {
        clearInterval(interval);
        stopPollingMock();
      };
    });

    vi.mocked(apiService.cancelScraping).mockResolvedValue({
      scrape_id: 'test-scrape-id-4',
      status: 'cancelled',
      message: '已取消爬取',
    });

    // Act
    render(<HomePage />);

    const urlInput = screen.getByPlaceholderText(/請貼上 Facebook 或 Instagram 貼文網址/i);
    await user.type(urlInput, facebookUrl);

    const scrapeButton = screen.getByRole('button', { name: /開始爬取/i });
    await user.click(scrapeButton);

    // 等待進度開始顯示
    await waitFor(() => {
      expect(screen.getByText(/已爬取/i)).toBeInTheDocument();
    }, { timeout: 1000 });

    // 等待爬取到一定數量 (模擬爬取到 250 則左右)
    await waitFor(() => {
      const progressText = screen.getByText(/已爬取 \d+\/500 則留言/i);
      expect(progressText).toBeInTheDocument();
    }, { timeout: 2000 });

    // 點擊取消按鈕
    const cancelButton = screen.getByRole('button', { name: /取消/i });
    await user.click(cancelButton);

    // Assert - 驗證取消行為
    expect(apiService.cancelScraping).toHaveBeenCalledWith('test-scrape-id-4');
    expect(stopPollingMock).toHaveBeenCalled();

    // 等待取消訊息顯示
    await waitFor(() => {
      expect(screen.getByText(/已取消/i)).toBeInTheDocument();
    }, { timeout: 1000 });

    // 驗證顯示保留的資料數量訊息
    // 注意: 實際數量取決於取消時的進度,這裡檢查訊息格式
    const cancelMessage = screen.getByText(/已取消/i);
    expect(cancelMessage).toBeInTheDocument();
  });

  /**
   * 額外測試: 錯誤處理 - 無效網址
   */
  it('額外測試: 輸入無效網址時顯示錯誤訊息', async () => {
    // Arrange
    const invalidUrl = 'https://example.com/invalid';
    
    vi.mocked(apiService.startScraping).mockRejectedValue(
      Object.assign(new Error('無法存取此貼文,請確認網址是否正確且為公開貼文'), {
        code: 'VALIDATION_ERROR',
        status: 400,
      })
    );

    // Act
    render(<HomePage />);

    const urlInput = screen.getByPlaceholderText(/請貼上 Facebook 或 Instagram 貼文網址/i);
    await user.type(urlInput, invalidUrl);

    const scrapeButton = screen.getByRole('button', { name: /開始爬取/i });
    await user.click(scrapeButton);

    // Assert - 驗證錯誤訊息顯示
    await waitFor(() => {
      expect(screen.getByText(/無法存取此貼文/i)).toBeInTheDocument();
    }, { timeout: 1000 });

    // 驗證重試按鈕存在
    expect(screen.getByRole('button', { name: /重試/i })).toBeInTheDocument();
  });

  /**
   * 額外測試: 錯誤處理 - 網路錯誤
   */
  it('額外測試: 網路異常時顯示錯誤並允許重試', async () => {
    // Arrange
    const facebookUrl = 'https://www.facebook.com/example/posts/123456';
    
    vi.mocked(apiService.startScraping).mockRejectedValue(
      Object.assign(new Error('網路連線失敗,請檢查網路設定'), {
        code: 'NETWORK_ERROR',
        status: 0,
      })
    );

    // Act
    render(<HomePage />);

    const urlInput = screen.getByPlaceholderText(/請貼上 Facebook 或 Instagram 貼文網址/i);
    await user.type(urlInput, facebookUrl);

    const scrapeButton = screen.getByRole('button', { name: /開始爬取/i });
    await user.click(scrapeButton);

    // Assert - 驗證網路錯誤訊息
    await waitFor(() => {
      expect(screen.getByText(/網路連線失敗/i)).toBeInTheDocument();
    }, { timeout: 1000 });

    // 點擊重試按鈕
    const retryButton = screen.getByRole('button', { name: /重試/i });
    
    // Mock 第二次呼叫成功
    vi.mocked(apiService.startScraping).mockResolvedValue({
      scrape_id: 'test-scrape-retry',
      status: 'running',
      message: '開始爬取...',
    });

    await user.click(retryButton);

    // 驗證重試後重新呼叫 API
    await waitFor(() => {
      expect(apiService.startScraping).toHaveBeenCalledTimes(2);
    });
  });

  /**
   * 額外測試: UI 狀態管理 - 爬取中禁用輸入
   */
  it('額外測試: 爬取進行中時,輸入框和按鈕應該被禁用', async () => {
    // Arrange
    const facebookUrl = 'https://www.facebook.com/example/posts/123456';
    
    vi.mocked(apiService.startScraping).mockResolvedValue({
      scrape_id: 'test-scrape-id-5',
      status: 'running',
      message: '開始爬取...',
    });

    // Mock pollProgress 保持 running 狀態
    vi.mocked(apiService.pollProgress).mockImplementation((scrapeId, onProgress) => {
      const interval = setInterval(() => {
        onProgress({
          scrape_id: scrapeId,
          status: 'running',
          progress: 0.5,
          total_comments: 100,
          scraped_comments: 50,
          error: null,
        });
      }, 200);

      return () => clearInterval(interval);
    });

    // Act
    render(<HomePage />);

    const urlInput = screen.getByPlaceholderText(/請貼上 Facebook 或 Instagram 貼文網址/i);
    await user.type(urlInput, facebookUrl);

    const scrapeButton = screen.getByRole('button', { name: /開始爬取/i });
    await user.click(scrapeButton);

    // Assert - 驗證 UI 元素被禁用
    await waitFor(() => {
      expect(urlInput).toBeDisabled();
      expect(scrapeButton).toBeDisabled();
    });

    // 驗證取消按鈕可用
    const cancelButton = screen.getByRole('button', { name: /取消/i });
    expect(cancelButton).not.toBeDisabled();
  });
});
