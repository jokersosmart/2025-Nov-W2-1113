/**
 * API Service
 * 
 * 提供與後端 API 通訊的服務函式
 * 
 * Features:
 * - Axios client with base URL
 * - startScraping(url) → POST /api/scrape
 * - getProgress(scraping_id) → GET /api/scrape/{id}/progress (with polling every 2s)
 * - cancelScraping(scraping_id) → POST /api/scrape/{id}/cancel
 * - exportToExcel(post, comments) → POST /api/export
 * - Error interceptor maps API errors to user messages
 * 
 * FR-006: 系統必須提供圖形化網頁介面
 * FR-008: 使用者必須能點擊按鈕觸發爬取動作
 * FR-019: 系統必須在爬取過程中顯示進度指示
 * FR-020: 使用者必須能在爬取過程中取消操作
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// API Base URL (from environment or default to localhost)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Polling interval for progress updates (milliseconds)
const PROGRESS_POLL_INTERVAL = 2000; // 2 seconds

/**
 * API Response Types
 */

export interface ScrapeResponse {
  scrape_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  message: string;
}

export interface ProgressResponse {
  scrape_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0.0 to 1.0
  total_comments: number;
  scraped_comments: number;
  error: string | null;
}

export interface CancelResponse {
  scrape_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  message: string;
}

export interface ApiError {
  error: string;
  message: string;
  details?: string;
}

/**
 * Create Axios instance
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Response interceptor for error handling
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    // Map API errors to user-friendly messages
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      
      // Extract user-friendly message
      const userMessage = data?.message || data?.error || '發生未知錯誤';
      
      // Create enhanced error
      const enhancedError = new Error(userMessage) as Error & {
        status: number;
        code: string;
        details?: string;
      };
      
      enhancedError.status = status;
      enhancedError.details = data?.details;
      
      // Map status codes to error codes
      switch (status) {
        case 400:
          enhancedError.code = 'VALIDATION_ERROR';
          break;
        case 403:
          enhancedError.code = 'AUTH_REQUIRED';
          break;
        case 404:
          enhancedError.code = 'NOT_FOUND';
          break;
        case 429:
          enhancedError.code = 'RATE_LIMIT';
          break;
        case 500:
        case 502:
        case 503:
          enhancedError.code = 'SERVER_ERROR';
          break;
        default:
          enhancedError.code = 'UNKNOWN_ERROR';
      }
      
      return Promise.reject(enhancedError);
    }
    
    if (error.request) {
      // Network error
      const networkError = new Error('網路連線失敗,請檢查網路設定') as Error & {
        status: number;
        code: string;
      };
      networkError.status = 0;
      networkError.code = 'NETWORK_ERROR';
      return Promise.reject(networkError);
    }
    
    // Other errors
    return Promise.reject(error);
  }
);

/**
 * API Service Functions
 */

/**
 * Start scraping a post
 * 
 * @param url - Post URL (Facebook or Instagram)
 * @returns Scrape job information
 */
export async function startScraping(url: string): Promise<ScrapeResponse> {
  const response = await apiClient.post<ScrapeResponse>('/api/scrape', { url });
  return response.data;
}

/**
 * Get scraping progress
 * 
 * @param scrapeId - Scrape job ID
 * @returns Progress information
 */
export async function getProgress(scrapeId: string): Promise<ProgressResponse> {
  const response = await apiClient.get<ProgressResponse>(`/api/scrape/${scrapeId}/progress`);
  return response.data;
}

/**
 * Cancel scraping job
 * 
 * @param scrapeId - Scrape job ID
 * @returns Cancel confirmation
 */
export async function cancelScraping(scrapeId: string): Promise<CancelResponse> {
  const response = await apiClient.post<CancelResponse>(`/api/scrape/${scrapeId}/cancel`);
  return response.data;
}

/**
 * Poll for progress updates
 * 
 * @param scrapeId - Scrape job ID
 * @param onProgress - Callback for each progress update
 * @param onComplete - Callback when scraping completes
 * @param onError - Callback when error occurs
 * @returns Stop function to cancel polling
 */
export function pollProgress(
  scrapeId: string,
  onProgress: (progress: ProgressResponse) => void,
  onComplete?: (progress: ProgressResponse) => void,
  onError?: (error: Error) => void
): () => void {
  let stopped = false;
  let timeoutId: NodeJS.Timeout;
  
  const poll = async () => {
    if (stopped) return;
    
    try {
      const progress = await getProgress(scrapeId);
      
      // Call progress callback
      onProgress(progress);
      
      // Check if completed
      const isTerminal = progress.status === 'completed' ||
                        progress.status === 'failed' ||
                        progress.status === 'cancelled';
      
      if (isTerminal) {
        if (onComplete) {
          onComplete(progress);
        }
        return; // Stop polling
      }
      
      // Schedule next poll
      if (!stopped) {
        timeoutId = setTimeout(poll, PROGRESS_POLL_INTERVAL);
      }
    } catch (error) {
      if (onError && !stopped) {
        onError(error as Error);
      }
      // Don't continue polling on error
    }
  };
  
  // Start polling
  poll();
  
  // Return stop function
  return () => {
    stopped = true;
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  };
}

/**
 * Export data to Excel
 * 
 * @param post - Post data
 * @param comments - Comments data
 * @returns Blob for download
 */
export async function exportToExcel(
  post: {
    platform: string;
    post_url: string;
    post_time: string;
    post_content: string;
    likes_count: number;
    comments_count: number;
  },
  comments: Array<{
    comment_id: string;
    post_url: string;
    comment_time: string;
    commenter_id: string;
    comment_content: string;
    reply_window?: string;
    reply_content?: string;
    customer_notes?: string;
    generated_reply?: string;
  }>
): Promise<Blob> {
  const response = await apiClient.post('/api/export', { post, comments }, {
    responseType: 'blob',
  });
  
  return response.data;
}

/**
 * Download blob as file
 * 
 * @param blob - Blob data
 * @param filename - Suggested filename
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

/**
 * Get API health status
 * 
 * @returns Health check response
 */
export async function getHealth(): Promise<{ status: string; version: string }> {
  const response = await apiClient.get('/health');
  return response.data;
}

export default {
  startScraping,
  getProgress,
  cancelScraping,
  pollProgress,
  exportToExcel,
  downloadBlob,
  getHealth,
};
