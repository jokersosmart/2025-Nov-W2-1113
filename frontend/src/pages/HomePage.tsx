/**
 * HomePage Component
 * 
 * 主頁面元件,整合所有功能:
 * - URL 輸入與平台偵測
 * - 爬取操作與進度追蹤
 * - 留言資料表格顯示與編輯
 * - 錯誤處理與使用者回饋
 * 
 * 使用者故事 1: 爬取單一貼文留言 (P1 - MVP)
 * 
 * 驗收情境:
 * 1. 使用者貼上 Facebook 公開貼文網址,系統顯示貼文資訊與留言列表
 * 2. 使用者貼上 Instagram 公開貼文網址,系統顯示貼文資訊與留言列表
 * 3. 貼文沒有留言時,顯示提示訊息
 * 4. 爬取過程中可取消操作,保留已爬取的部分資料
 * 
 * FR-006: 系統必須提供圖形化網頁介面
 * FR-007: 使用者必須能透過輸入框貼上目標貼文網址
 * FR-008: 使用者必須能點擊按鈕觸發爬取動作
 * FR-009: 系統必須以表格形式顯示爬取到的資料
 * FR-019: 系統必須在爬取過程中顯示進度指示
 * FR-020: 使用者必須能在爬取過程中取消操作
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import { useState, useCallback, useEffect } from 'react';
import { useStore } from '../services/store';
import { UrlInput } from '../components/UrlInput';
import { ScrapeButton } from '../components/ScrapeButton';
import { ProgressIndicator } from '../components/ProgressIndicator';
import { CommentTable } from '../components/CommentTable';
import { ErrorMessage } from '../components/ErrorMessage';
import { startScraping, pollProgress, cancelScraping } from '../services/apiService';
import type { Platform } from '../types/post';

/**
 * HomePage Component
 */
export function HomePage(): JSX.Element {
  // Local state for URL input
  const [url, setUrl] = useState('');
  const [platform, setPlatform] = useState<Platform | null>(null);
  
  // Local state for comment selection (US2)
  const [selectedCommentIds, setSelectedCommentIds] = useState<Set<string>>(new Set());

  // Global state from Zustand store
  const {
    post,
    comments,
    scrapeProgress,
    error,
    setScrapeProgress,
    updateScrapeProgress,
    updateComment,
    deleteComments,
    setError,
    reset,
  } = useStore();

  // Polling stop function ref
  const [stopPolling, setStopPolling] = useState<(() => void) | null>(null);

  /**
   * Handle URL change from UrlInput
   */
  const handleUrlChange = useCallback((newUrl: string) => {
    setUrl(newUrl);
    // Detect platform from URL
    const lowerUrl = newUrl.toLowerCase();
    let detectedPlatform: Platform | null = null;
    
    if (lowerUrl.includes('facebook.com') || lowerUrl.includes('fb.com')) {
      detectedPlatform = 'facebook';
    } else if (lowerUrl.includes('instagram.com')) {
      detectedPlatform = 'instagram';
    }
    
    setPlatform(detectedPlatform);
    setError(null); // Clear previous errors
  }, [setError]);

  /**
   * Handle scraping start
   */
  const handleStartScraping = useCallback(async () => {
    if (!url || !platform) {
      setError('請輸入有效的 Facebook 或 Instagram 貼文網址');
      return;
    }

    try {
      // Reset previous state
      reset();
      setError(null);

      // Start scraping
      const response = await startScraping(url);

      // Initialize scrape progress
      setScrapeProgress({
        scrapeId: response.scrape_id,
        status: 'scraping',
        progress: 0,
        totalComments: 0,
        scrapedComments: 0,
        message: response.message || '開始爬取...',
      });

      // Start polling for progress
      const stop = pollProgress(
        response.scrape_id,
        // onProgress callback
        (progress) => {
          // Map API status to store status
          let status: 'idle' | 'scraping' | 'completed' | 'failed' | 'cancelled' = 'scraping';
          if (progress.status === 'completed') status = 'completed';
          else if (progress.status === 'failed') status = 'failed';
          else if (progress.status === 'cancelled') status = 'cancelled';
          
          updateScrapeProgress({
            status,
            progress: Math.round(progress.progress * 100),
            totalComments: progress.total_comments,
            scrapedComments: progress.scraped_comments,
            message: `已爬取 ${progress.scraped_comments} / ${progress.total_comments} 則留言`,
          });

          // If completed, fetch final data
          if (progress.status === 'completed') {
            // In a real implementation, you'd fetch the complete data here
            // For now, we'll simulate it based on the progress
            // TODO: Add API endpoint to fetch complete scraping result
          }
        },
        // onComplete callback
        (progress) => {
          if (progress.status === 'completed') {
            updateScrapeProgress({
              status: 'completed',
              progress: 100,
              message: `完成! 成功爬取 ${progress.scraped_comments} 則留言`,
            });
          } else if (progress.status === 'failed') {
            updateScrapeProgress({
              status: 'failed',
              message: progress.error || '爬取失敗',
            });
            setError(progress.error || '爬取過程發生錯誤');
          } else if (progress.status === 'cancelled') {
            updateScrapeProgress({
              status: 'cancelled',
              message: `已取消,保留 ${progress.scraped_comments} 則留言資料`,
            });
          }
        },
        // onError callback
        (error) => {
          setScrapeProgress({
            scrapeId: response.scrape_id,
            status: 'failed',
            progress: 0,
            totalComments: 0,
            scrapedComments: 0,
            message: '進度查詢失敗',
          });
          setError(error.message || '無法取得爬取進度');
        }
      );

      setStopPolling(() => stop);
    } catch (error) {
      const err = error as Error & { code?: string };
      setError(err.message || '啟動爬取失敗');
      setScrapeProgress(null);
    }
  }, [url, platform, reset, setError, setScrapeProgress, updateScrapeProgress]);

  /**
   * Handle scraping cancellation
   */
  const handleCancelScraping = useCallback(async () => {
    if (!scrapeProgress?.scrapeId) return;

    try {
      // Stop polling first
      if (stopPolling) {
        stopPolling();
        setStopPolling(null);
      }

      // Send cancel request
      await cancelScraping(scrapeProgress.scrapeId);

      // Update status
      updateScrapeProgress({
        status: 'cancelled',
        message: `已取消,保留 ${scrapeProgress.scrapedComments} 則留言資料`,
      });
    } catch (error) {
      const err = error as Error;
      setError(err.message || '取消爬取失敗');
    }
  }, [scrapeProgress, stopPolling, updateScrapeProgress, setError]);

  /**
   * Handle error retry
   */
  const handleRetry = useCallback(() => {
    setError(null);
    if (url && platform) {
      handleStartScraping();
    }
  }, [url, platform, handleStartScraping, setError]);

  /**
   * Handle error dismiss
   */
  const handleDismissError = useCallback(() => {
    setError(null);
  }, [setError]);

  /**
   * Handle comment field edit (US2)
   * FR-010: 使用者必須能編輯表格中的欄位
   */
  const handleCommentEdit = useCallback((commentId: string, field: string, value: string) => {
    updateComment(commentId, { [field]: value });
  }, [updateComment]);

  /**
   * Handle comment selection change (US2)
   */
  const handleSelectionChange = useCallback((newSelection: Set<string>) => {
    setSelectedCommentIds(newSelection);
  }, []);

  /**
   * Handle delete selected comments (US2)
   * FR-011: 使用者必須能勾選並刪除不需要的留言資料列
   */
  const handleDeleteSelected = useCallback(() => {
    if (selectedCommentIds.size === 0) return;
    
    if (window.confirm(`確定要刪除 ${selectedCommentIds.size} 則留言嗎?此操作無法復原。`)) {
      deleteComments(Array.from(selectedCommentIds));
      setSelectedCommentIds(new Set()); // Clear selection
    }
  }, [selectedCommentIds, deleteComments]);

  /**
   * Cleanup polling on unmount
   */
  useEffect(() => {
    return () => {
      if (stopPolling) {
        stopPolling();
      }
    };
  }, [stopPolling]);

  // Determine if scraping is in progress
  const isScraping = scrapeProgress?.status === 'scraping';

  // Check if we have no comments (after successful scrape)
  const hasNoComments = 
    scrapeProgress?.status === 'completed' && 
    comments.length === 0;

  return (
    <div className="home-page" style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
          社群平台留言爬蟲工具
        </h1>
        <p style={{ color: '#666', fontSize: '1rem' }}>
          從 Facebook 或 Instagram 公開貼文爬取留言資料
        </p>
      </header>

      {/* Input Section */}
      <section 
        style={{ 
          backgroundColor: '#f9fafb', 
          padding: '1.5rem', 
          borderRadius: '0.5rem',
          marginBottom: '2rem',
        }}
        aria-label="爬取設定"
      >
        <div style={{ marginBottom: '1rem' }}>
          <UrlInput
            value={url}
            onChange={handleUrlChange}
            disabled={isScraping}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <ScrapeButton
            onClick={handleStartScraping}
            disabled={!url || !platform || isScraping}
            loading={isScraping}
          />

          {platform && (
            <span style={{ color: '#666', fontSize: '0.875rem' }}>
              偵測到平台: <strong>{platform === 'facebook' ? 'Facebook' : 'Instagram'}</strong>
            </span>
          )}
        </div>
      </section>

      {/* Error Message */}
      {error && (
        <div style={{ marginBottom: '2rem' }}>
          <ErrorMessage
            message={error}
            onRetry={handleRetry}
            onDismiss={handleDismissError}
          />
        </div>
      )}

      {/* Progress Indicator */}
      {scrapeProgress && (
        <div style={{ marginBottom: '2rem' }}>
          <ProgressIndicator
            current={scrapeProgress.scrapedComments}
            total={scrapeProgress.totalComments}
            status={
              scrapeProgress.status === 'idle' ? 'pending' : 
              scrapeProgress.status === 'scraping' ? 'running' :
              scrapeProgress.status
            }
            showCancel={isScraping}
            onCancel={isScraping ? handleCancelScraping : undefined}
          />
        </div>
      )}

      {/* Post Information */}
      {post && (
        <section 
          style={{ 
            backgroundColor: '#f0f9ff', 
            padding: '1.5rem', 
            borderRadius: '0.5rem',
            marginBottom: '2rem',
          }}
          aria-label="貼文資訊"
        >
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            貼文資訊
          </h2>
          <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.5rem 1rem', fontSize: '0.875rem' }}>
            <dt style={{ fontWeight: '600' }}>平台:</dt>
            <dd>{post.platform === 'facebook' ? 'Facebook' : 'Instagram'}</dd>
            
            <dt style={{ fontWeight: '600' }}>發文時間:</dt>
            <dd>{new Date(post.post_time).toLocaleString('zh-TW')}</dd>
            
            <dt style={{ fontWeight: '600' }}>按讚數:</dt>
            <dd>{post.likes_count.toLocaleString()}</dd>
            
            <dt style={{ fontWeight: '600' }}>留言總數:</dt>
            <dd>{post.comments_count.toLocaleString()}</dd>
            
            <dt style={{ fontWeight: '600' }}>貼文內容:</dt>
            <dd style={{ whiteSpace: 'pre-wrap' }}>{post.post_content}</dd>
            
            <dt style={{ fontWeight: '600' }}>貼文連結:</dt>
            <dd>
              <a 
                href={post.post_url} 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#0066cc', textDecoration: 'underline' }}
              >
                {post.post_url}
              </a>
            </dd>
          </dl>
        </section>
      )}

      {/* No Comments Message */}
      {hasNoComments && (
        <div 
          style={{ 
            backgroundColor: '#fffbeb', 
            padding: '1.5rem', 
            borderRadius: '0.5rem',
            marginBottom: '2rem',
            textAlign: 'center',
          }}
          role="status"
          aria-live="polite"
        >
          <p style={{ color: '#92400e', fontSize: '1rem' }}>
            ℹ️ 此貼文尚無留言
          </p>
        </div>
      )}

      {/* Comments Table */}
      {comments.length > 0 && (
        <section aria-label="留言列表">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>
              留言列表 ({comments.length} 則)
            </h2>
            
            {/* Delete button (US2) */}
            {selectedCommentIds.size > 0 && (
              <button
                onClick={handleDeleteSelected}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#dc2626',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.375rem',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                }}
                onMouseEnter={(e) => {
                  (e.target as HTMLButtonElement).style.backgroundColor = '#b91c1c';
                }}
                onMouseLeave={(e) => {
                  (e.target as HTMLButtonElement).style.backgroundColor = '#dc2626';
                }}
                aria-label={`刪除 ${selectedCommentIds.size} 則留言`}
              >
                🗑️ 刪除選取的留言 ({selectedCommentIds.size})
              </button>
            )}
          </div>
          
          <CommentTable 
            comments={comments}
            selectable={true}
            selectedIds={selectedCommentIds}
            onSelectionChange={handleSelectionChange}
            editable={true}
            onEdit={handleCommentEdit}
          />
        </section>
      )}

      {/* Empty State (no scraping started yet) */}
      {!scrapeProgress && !post && !error && (
        <div 
          style={{ 
            textAlign: 'center', 
            padding: '4rem 2rem',
            color: '#9ca3af',
          }}
        >
          <p style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>
            👆 請在上方輸入 Facebook 或 Instagram 貼文網址開始爬取
          </p>
          <p style={{ fontSize: '0.875rem' }}>
            支援公開貼文的第一層留言爬取
          </p>
        </div>
      )}
    </div>
  );
}

export default HomePage;
