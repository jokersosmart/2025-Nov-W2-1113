/**
 * Scrape Button Component
 * 
 * 觸發爬取操作的按鈕元件
 * 
 * Features:
 * - Triggers scrape API call
 * - Disables during scraping
 * - Shows loading state
 * - Accessible with aria-busy during loading
 * - Keyboard support (Enter/Space)
 * 
 * FR-008: 使用者必須能點擊按鈕觸發爬取動作
 * FR-019: 系統必須在爬取過程中顯示進度指示
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import React, { useCallback } from 'react';

export interface ScrapeButtonProps {
  /** Click handler */
  onClick: () => void | Promise<void>;
  /** Loading state */
  loading?: boolean;
  /** Disabled state */
  disabled?: boolean;
  /** Button text */
  children?: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * ScrapeButton Component
 */
export const ScrapeButton: React.FC<ScrapeButtonProps> = ({
  onClick,
  loading = false,
  disabled = false,
  children = '開始爬取',
  className = '',
}) => {
  const isDisabled = disabled || loading;
  
  const handleClick = useCallback(async () => {
    if (isDisabled) return;
    
    try {
      await onClick();
    } catch (error) {
      console.error('Scrape button click error:', error);
    }
  }, [onClick, isDisabled]);
  
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLButtonElement>) => {
    // Enter and Space trigger button
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }, [handleClick]);
  
  return (
    <button
      type="button"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={isDisabled}
      aria-busy={loading}
      aria-label={loading ? '爬取中...' : '開始爬取留言'}
      className={`scrape-button ${loading ? 'scrape-button-loading' : ''} ${
        isDisabled ? 'scrape-button-disabled' : ''
      } ${className}`}
    >
      {loading && (
        <span className="scrape-button-spinner" aria-hidden="true">
          <svg
            className="spinner"
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle
              className="spinner-circle"
              cx="8"
              cy="8"
              r="6"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeDasharray="30 10"
            />
          </svg>
        </span>
      )}
      
      <span className="scrape-button-text">
        {loading ? '爬取中...' : children}
      </span>
    </button>
  );
};

export default ScrapeButton;
