/**
 * Error Message Component
 * 
 * 顯示友善錯誤訊息的元件
 * 
 * Features:
 * - Displays user-friendly error from API
 * - Different styling for validation/network/server errors
 * - Shows retry action for network errors
 * - Accessible with role="alert"
 * - Auto-dismiss option
 * - Stack multiple errors
 * 
 * FR-014: 系統必須在無法存取貼文時顯示友善的錯誤訊息
 * FR-015: 系統必須在網路異常時顯示錯誤訊息並允許重試
 * FR-016: 系統必須處理貼文無留言的情況並顯示提示訊息
 * FR-025: 系統必須在偵測到平台速率限制或反爬蟲機制時停止爬取並顯示友善錯誤訊息
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import React, { useCallback } from 'react';

export type ErrorType = 
  | 'validation'  // 驗證錯誤 (400)
  | 'auth'        // 需要驗證 (403)
  | 'notfound'    // 找不到 (404)
  | 'ratelimit'   // 速率限制 (429)
  | 'network'     // 網路錯誤
  | 'server'      // 伺服器錯誤 (500)
  | 'unknown';    // 未知錯誤

export interface ErrorMessageProps {
  /** Error message to display */
  message: string;
  /** Error type */
  type?: ErrorType;
  /** Technical details (optional, shown in collapsible section) */
  details?: string;
  /** Retry action handler */
  onRetry?: () => void | Promise<void>;
  /** Dismiss handler */
  onDismiss?: () => void;
  /** Auto-dismiss after seconds (0 = no auto-dismiss) */
  autoDismiss?: number;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Get error type icon
 */
function getErrorIcon(type: ErrorType): string {
  switch (type) {
    case 'validation':
      return '⚠️';
    case 'auth':
      return '🔒';
    case 'notfound':
      return '❓';
    case 'ratelimit':
      return '⏱️';
    case 'network':
      return '🌐';
    case 'server':
      return '❌';
    default:
      return '❗';
  }
}

/**
 * Get error type label
 */
function getErrorLabel(type: ErrorType): string {
  switch (type) {
    case 'validation':
      return '驗證錯誤';
    case 'auth':
      return '需要登入';
    case 'notfound':
      return '找不到資源';
    case 'ratelimit':
      return '請求次數過多';
    case 'network':
      return '網路錯誤';
    case 'server':
      return '伺服器錯誤';
    default:
      return '錯誤';
  }
}

/**
 * Get suggested action text
 */
function getSuggestedAction(type: ErrorType): string | null {
  switch (type) {
    case 'validation':
      return '請檢查輸入的網址格式是否正確';
    case 'auth':
      return '此貼文需要登入才能存取,請確認為公開貼文';
    case 'notfound':
      return '貼文可能已被刪除或設為私人';
    case 'ratelimit':
      return '請稍後再試,或降低爬取頻率';
    case 'network':
      return '請檢查網路連線,稍後重試';
    case 'server':
      return '伺服器暫時無法處理請求,請稍後再試';
    default:
      return null;
  }
}

/**
 * ErrorMessage Component
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  type = 'unknown',
  details,
  onRetry,
  onDismiss,
  autoDismiss = 0,
  className = '',
}) => {
  const [showDetails, setShowDetails] = React.useState(false);
  const [isRetrying, setIsRetrying] = React.useState(false);
  
  // Auto-dismiss timer
  React.useEffect(() => {
    if (autoDismiss > 0 && onDismiss) {
      const timer = setTimeout(() => {
        onDismiss();
      }, autoDismiss * 1000);
      
      return () => clearTimeout(timer);
    }
  }, [autoDismiss, onDismiss]);
  
  const handleRetry = useCallback(async () => {
    if (!onRetry || isRetrying) return;
    
    setIsRetrying(true);
    try {
      await onRetry();
    } catch (error) {
      console.error('Retry failed:', error);
    } finally {
      setIsRetrying(false);
    }
  }, [onRetry, isRetrying]);
  
  const toggleDetails = useCallback(() => {
    setShowDetails(prev => !prev);
  }, []);
  
  const icon = getErrorIcon(type);
  const label = getErrorLabel(type);
  const suggestedAction = getSuggestedAction(type);
  const showRetry = type === 'network' || type === 'ratelimit' || type === 'server';
  
  return (
    <div
      className={`error-message error-message-${type} ${className}`}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div className="error-header">
        <span className="error-icon" aria-hidden="true">
          {icon}
        </span>
        <span className="error-label">{label}</span>
        
        {onDismiss && (
          <button
            type="button"
            onClick={onDismiss}
            className="error-dismiss"
            aria-label="關閉錯誤訊息"
          >
            ✕
          </button>
        )}
      </div>
      
      <div className="error-body">
        <p className="error-message-text">{message}</p>
        
        {suggestedAction && (
          <p className="error-suggestion">
            💡 {suggestedAction}
          </p>
        )}
        
        {details && (
          <div className="error-details-section">
            <button
              type="button"
              onClick={toggleDetails}
              className="error-details-toggle"
              aria-expanded={showDetails}
              aria-controls="error-details-content"
            >
              {showDetails ? '▼' : '▶'} 技術細節
            </button>
            
            {showDetails && (
              <pre
                id="error-details-content"
                className="error-details-content"
                aria-label="錯誤技術細節"
              >
                {details}
              </pre>
            )}
          </div>
        )}
      </div>
      
      {(showRetry && onRetry) && (
        <div className="error-actions">
          <button
            type="button"
            onClick={handleRetry}
            disabled={isRetrying}
            className="error-retry-button"
            aria-busy={isRetrying}
          >
            {isRetrying ? '重試中...' : '重試'}
          </button>
        </div>
      )}
    </div>
  );
};

export default ErrorMessage;
