/**
 * Progress Indicator Component
 * 
 * 顯示爬取進度的元件
 * 
 * Features:
 * - Displays progress bar with current/total
 * - Shows percentage and text "已爬取 X/Y 則留言"
 * - Updates in real-time from progress API polling
 * - Accessible with aria-live for screen readers
 * - Shows estimated time remaining (optional)
 * 
 * FR-019: 系統必須在爬取過程中顯示進度指示
 * SC-008: 爬取超過100則留言時,使用者能在畫面上即時看到進度更新
 * SC-009: 使用者能在3秒內理解當前爬取進度
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import React, { useMemo } from 'react';

export interface ProgressIndicatorProps {
  /** Current progress (scraped comments) */
  current: number;
  /** Total comments */
  total: number;
  /** Status of scraping job */
  status?: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  /** Show cancel button */
  showCancel?: boolean;
  /** Cancel handler */
  onCancel?: () => void | Promise<void>;
  /** Additional CSS classes */
  className?: string;
}

/**
 * ProgressIndicator Component
 */
export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  current,
  total,
  status = 'running',
  showCancel = false,
  onCancel,
  className = '',
}) => {
  // Calculate percentage (0-100)
  const percentage = useMemo(() => {
    if (total === 0) return 0;
    return Math.min(Math.round((current / total) * 100), 100);
  }, [current, total]);
  
  // Status message
  const statusMessage = useMemo(() => {
    switch (status) {
      case 'pending':
        return '準備中...';
      case 'running':
        return `已爬取 ${current}/${total} 則留言`;
      case 'completed':
        return `完成! 共爬取 ${current} 則留言`;
      case 'failed':
        return '爬取失敗';
      case 'cancelled':
        return `已取消,保留 ${current} 則留言資料`;
      default:
        return '';
    }
  }, [status, current, total]);
  
  // Status color
  const statusColor = useMemo(() => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'cancelled':
        return 'warning';
      default:
        return 'info';
    }
  }, [status]);
  
  const handleCancel = async () => {
    if (onCancel) {
      try {
        await onCancel();
      } catch (error) {
        console.error('Cancel error:', error);
      }
    }
  };
  
  const isActive = status === 'pending' || status === 'running';
  
  return (
    <div className={`progress-indicator progress-indicator-${statusColor} ${className}`} role="region" aria-label="爬取進度">
      {/* Status message */}
      <div className="progress-message" aria-live="polite" aria-atomic="true">
        <span className="progress-status-text">{statusMessage}</span>
        {isActive && (
          <span className="progress-percentage" aria-label={`完成度 ${percentage}%`}>
            {percentage}%
          </span>
        )}
      </div>
      
      {/* Progress bar */}
      <div className="progress-bar-container" role="progressbar" aria-valuenow={percentage} aria-valuemin={0} aria-valuemax={100} aria-label="爬取進度條">
        <div
          className={`progress-bar ${isActive ? 'progress-bar-active' : ''}`}
          style={{ width: `${percentage}%` }}
        >
          {isActive && <div className="progress-bar-animation" />}
        </div>
      </div>
      
      {/* Cancel button (FR-020) */}
      {showCancel && isActive && onCancel && (
        <div className="progress-actions">
          <button
            type="button"
            onClick={handleCancel}
            className="progress-cancel-button"
            aria-label="取消爬取"
          >
            取消爬取
          </button>
          <span className="progress-cancel-hint" aria-live="polite">
            取消後會保留已爬取的資料
          </span>
        </div>
      )}
      
      {/* Additional info */}
      {total > 0 && (
        <div className="progress-details" aria-live="polite">
          <span className="progress-detail-item">
            總留言數: {total}
          </span>
          <span className="progress-detail-item">
            已爬取: {current}
          </span>
          <span className="progress-detail-item">
            剩餘: {Math.max(0, total - current)}
          </span>
        </div>
      )}
    </div>
  );
};

export default ProgressIndicator;
