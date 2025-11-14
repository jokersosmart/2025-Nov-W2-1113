/**
 * URL Input Component
 * 
 * 輸入框元件,供使用者貼上 Facebook/Instagram 貼文網址
 * 
 * Features:
 * - Auto-detect platform from URL
 * - Validate URL format on blur
 * - Show validation error if invalid
 * - Accessible with aria-label and keyboard support
 * 
 * FR-007: 使用者必須能透過輸入框貼上目標貼文網址
 * FR-014: 系統必須在無法存取貼文時顯示友善的錯誤訊息
 * 
 * @author COM_PAR Team
 * @date 2025-11-15
 */

import React, { useState, useCallback } from 'react';

export interface UrlInputProps {
  /** URL value */
  value: string;
  /** Change handler */
  onChange: (value: string) => void;
  /** Validation error message */
  error?: string;
  /** Disabled state */
  disabled?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Detect platform from URL
 */
function detectPlatform(url: string): 'facebook' | 'instagram' | 'unknown' {
  if (!url) return 'unknown';
  
  const lowerUrl = url.toLowerCase();
  
  if (lowerUrl.includes('facebook.com') || lowerUrl.includes('fb.com')) {
    return 'facebook';
  }
  
  if (lowerUrl.includes('instagram.com')) {
    return 'instagram';
  }
  
  return 'unknown';
}

/**
 * Validate URL format (basic client-side validation)
 */
function validateUrlFormat(url: string): { isValid: boolean; message?: string } {
  if (!url.trim()) {
    return { isValid: false, message: '請輸入網址' };
  }
  
  // Basic URL format check
  try {
    new URL(url);
  } catch {
    return { isValid: false, message: '網址格式不正確' };
  }
  
  const platform = detectPlatform(url);
  
  if (platform === 'unknown') {
    return {
      isValid: false,
      message: '僅支援 Facebook 和 Instagram 貼文網址'
    };
  }
  
  // Facebook URL patterns
  if (platform === 'facebook') {
    const fbPatterns = [
      /facebook\.com\/[^/]+\/posts\//,
      /facebook\.com\/photo/,
      /facebook\.com\/permalink\.php/,
      /fb\.com\//
    ];
    
    const isValidFb = fbPatterns.some(pattern => pattern.test(url));
    if (!isValidFb) {
      return {
        isValid: false,
        message: 'Facebook 網址格式不正確 (需為貼文連結)'
      };
    }
  }
  
  // Instagram URL patterns
  if (platform === 'instagram') {
    const igPattern = /instagram\.com\/p\/[A-Za-z0-9_-]+/;
    
    if (!igPattern.test(url)) {
      return {
        isValid: false,
        message: 'Instagram 網址格式不正確 (需為貼文連結)'
      };
    }
  }
  
  return { isValid: true };
}

/**
 * UrlInput Component
 */
export const UrlInput: React.FC<UrlInputProps> = ({
  value,
  onChange,
  error: externalError,
  disabled = false,
  placeholder = '請貼上 Facebook 或 Instagram 貼文網址',
  className = '',
}) => {
  const [internalError, setInternalError] = useState<string>('');
  const [platform, setPlatform] = useState<'facebook' | 'instagram' | 'unknown'>('unknown');
  
  // Use external error if provided, otherwise use internal error
  const displayError = externalError || internalError;
  
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    
    // Clear internal error on change
    setInternalError('');
    
    // Detect platform
    const detectedPlatform = detectPlatform(newValue);
    setPlatform(detectedPlatform);
  }, [onChange]);
  
  const handleBlur = useCallback(() => {
    if (!value.trim()) {
      setInternalError('');
      setPlatform('unknown');
      return;
    }
    
    const validation = validateUrlFormat(value);
    if (!validation.isValid && validation.message) {
      setInternalError(validation.message);
    } else {
      setInternalError('');
    }
  }, [value]);
  
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    // Enter key to submit (handled by parent form)
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
    
    // Escape key to clear
    if (e.key === 'Escape') {
      onChange('');
      setInternalError('');
      setPlatform('unknown');
    }
  }, [onChange]);
  
  return (
    <div className={`url-input-container ${className}`}>
      <div className="url-input-wrapper">
        <input
          type="url"
          value={value}
          onChange={handleChange}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          aria-label="貼文網址輸入框"
          aria-invalid={!!displayError}
          aria-describedby={displayError ? 'url-error' : undefined}
          className={`url-input ${displayError ? 'url-input-error' : ''} ${
            platform !== 'unknown' ? `url-input-${platform}` : ''
          }`}
        />
        
        {platform !== 'unknown' && !displayError && (
          <span className={`platform-badge platform-badge-${platform}`} aria-label={`平台: ${platform}`}>
            {platform === 'facebook' ? 'Facebook' : 'Instagram'}
          </span>
        )}
      </div>
      
      {displayError && (
        <div id="url-error" className="url-error" role="alert">
          {displayError}
        </div>
      )}
    </div>
  );
};

export default UrlInput;
