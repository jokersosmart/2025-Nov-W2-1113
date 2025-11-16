/**
 * Export Button Component
 * 
 * 觸發匯出 Excel 操作的按鈕元件
 * 
 * Features:
 * - Triggers export API call
 * - Shows loading state during export
 * - Handles download success/failure
 * - Accessible with aria-busy during loading
 * - Keyboard support (Enter/Space)
 * 
 * FR-012: 使用者必須能點擊按鈕匯出資料為 Excel 檔案
 * FR-013: 系統必須生成符合格式的 Excel 檔案(包含所有必要欄位)
 * 
 * @author COM_PAR Team
 * @date 2025-11-16
 */

import React, { useCallback, useState } from 'react';

export interface ExportButtonProps {
  /** Click handler that triggers export */
  onClick: () => void | Promise<void>;
  /** Disabled state (e.g., when no data available) */
  disabled?: boolean;
  /** Button text */
  children?: React.ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * ExportButton Component
 * 
 * @example
 * ```tsx
 * <ExportButton 
 *   onClick={handleExport} 
 *   disabled={!hasData}
 * >
 *   匯出 Excel
 * </ExportButton>
 * ```
 */
export const ExportButton: React.FC<ExportButtonProps> = ({
  onClick,
  disabled = false,
  children = '匯出 Excel',
  className = '',
}) => {
  const [loading, setLoading] = useState(false);
  
  const handleClick = useCallback(async () => {
    if (disabled || loading) return;
    
    setLoading(true);
    try {
      await onClick();
    } catch (error) {
      console.error('Export button click error:', error);
      // Error handling is done by the parent component
    } finally {
      setLoading(false);
    }
  }, [onClick, disabled, loading]);
  
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLButtonElement>) => {
    // Enter and Space trigger button
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }, [handleClick]);
  
  const isDisabled = disabled || loading;
  
  return (
    <button
      type="button"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={isDisabled}
      aria-busy={loading}
      aria-label={loading ? '匯出中...' : '匯出 Excel 檔案'}
      className={`export-button ${loading ? 'export-button-loading' : ''} ${
        isDisabled ? 'export-button-disabled' : ''
      } ${className}`}
    >
      {loading && (
        <span className="export-button-spinner" aria-hidden="true">
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
      
      {!loading && (
        <span className="export-button-icon" aria-hidden="true">
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M8 10L4 6h2.5V2h3v4H12L8 10z"
              fill="currentColor"
            />
            <path
              d="M14 10v4H2v-4H0v4a2 2 0 002 2h12a2 2 0 002-2v-4h-2z"
              fill="currentColor"
            />
          </svg>
        </span>
      )}
      
      <span className="export-button-text">
        {loading ? '匯出中...' : children}
      </span>
    </button>
  );
};

export default ExportButton;
