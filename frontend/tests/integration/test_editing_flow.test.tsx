/**
 * E2E Integration Tests - 編輯流程
 * 
 * 測試使用者故事 2 (P2) 的線上編輯功能
 * 
 * 驗收情境:
 * 1. 使用者點擊「回覆窗口」欄位並輸入文字,欄位立即更新
 * 2. 使用者點擊「回覆內容」欄位並輸入文字,欄位立即更新
 * 3. 使用者勾選一或多列留言並點擊「刪除」,被勾選的列從表格中移除
 * 4. 使用者編輯部分欄位後重新整理頁面,編輯內容不會保留
 * 
 * FR-010: 使用者必須能編輯表格中的「回覆窗口」、「回覆內容」、「客戶確認/修改處」欄位
 * FR-011: 使用者必須能勾選並刪除不需要的留言資料列
 * 
 * @author COM_PAR Team
 * @date 2025-11-16
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { HomePage } from '../../src/pages/HomePage';
import { useStore } from '../../src/services/store';
import type { Comment } from '../../src/types/comment';
import type { Post } from '../../src/types/post';

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

describe('編輯流程 E2E 測試', () => {
  let user: ReturnType<typeof userEvent.setup>;

  // 測試資料
  const mockPost: Post = {
    post_url: 'https://www.facebook.com/example/posts/123456789',
    platform: 'facebook',
    post_time: '2025-11-15T10:30:00Z',
    post_content: '這是測試貼文內容',
    likes_count: 100,
    comments_count: 3,
  };

  const mockComments: Comment[] = [
    {
      comment_id: 'comment-1',
      post_url: mockPost.post_url,
      comment_time: '2025-11-15T10:35:00Z',
      commenter_id: 'John Doe (12345678)',
      comment_content: '這是第一則留言',
      reply_window: null,
      reply_content: null,
      customer_notes: null,
      generated_reply: null,
    },
    {
      comment_id: 'comment-2',
      post_url: mockPost.post_url,
      comment_time: '2025-11-15T10:40:00Z',
      commenter_id: 'Jane Smith (87654321)',
      comment_content: '這是第二則留言',
      reply_window: null,
      reply_content: null,
      customer_notes: null,
      generated_reply: null,
    },
    {
      comment_id: 'comment-3',
      post_url: mockPost.post_url,
      comment_time: '2025-11-15T10:45:00Z',
      commenter_id: 'Bob Wilson (11111111)',
      comment_content: '這是第三則留言',
      reply_window: null,
      reply_content: null,
      customer_notes: null,
      generated_reply: null,
    },
  ];

  beforeEach(() => {
    user = userEvent.setup();
    vi.clearAllMocks();
    
    // Mock window.confirm
    window.confirm = vi.fn();
    
    // 重置 Zustand store 並設置測試資料
    const store = useStore.getState();
    store.reset();
    store.setPost(mockPost);
    store.setComments(mockComments);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * 驗收情境 1: 編輯「回覆窗口」欄位
   * 
   * Given: 系統已成功爬取並顯示留言資料表格
   * When: 使用者點擊某一列的「回覆窗口」欄位並輸入文字(如「張小明」)
   * Then: 該欄位立即更新為使用者輸入的內容
   */
  it('驗收情境 1: 使用者編輯回覆窗口欄位,欄位立即更新', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 找到第一列的「回覆窗口」輸入框
    const replyWindowInputs = screen.getAllByPlaceholderText('輸入回覆窗口');
    expect(replyWindowInputs.length).toBe(3); // 3 則留言

    const firstReplyWindowInput = replyWindowInputs[0] as HTMLInputElement;
    
    // 輸入文字
    await user.clear(firstReplyWindowInput);
    await user.type(firstReplyWindowInput, '張小明');

    // Assert - 驗證欄位更新
    await waitFor(() => {
      expect(firstReplyWindowInput.value).toBe('張小明');
    });

    // 驗證 store 中的資料已更新
    const updatedComments = useStore.getState().comments;
    expect(updatedComments[0].reply_window).toBe('張小明');
  });

  /**
   * 驗收情境 2: 編輯「回覆內容」欄位
   * 
   * Given: 系統已成功爬取並顯示留言資料表格
   * When: 使用者點擊某一列的「回覆內容」欄位並輸入文字
   * Then: 該欄位立即更新為使用者輸入的內容
   */
  it('驗收情境 2: 使用者編輯回覆內容欄位,欄位立即更新', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 找到第二列的「回覆內容」輸入框
    const replyContentInputs = screen.getAllByPlaceholderText('輸入回覆內容');
    expect(replyContentInputs.length).toBe(3);

    const secondReplyContentInput = replyContentInputs[1] as HTMLTextAreaElement;
    
    // 輸入文字
    await user.clear(secondReplyContentInput);
    await user.type(secondReplyContentInput, '感謝您的留言,我們會盡快回覆');

    // Assert - 驗證欄位更新
    await waitFor(() => {
      expect(secondReplyContentInput.value).toBe('感謝您的留言,我們會盡快回覆');
    });

    // 驗證 store 中的資料已更新
    const updatedComments = useStore.getState().comments;
    expect(updatedComments[1].reply_content).toBe('感謝您的留言,我們會盡快回覆');
  });

  /**
   * 驗收情境 2 (延伸): 編輯「客戶確認/修改處」欄位
   * 
   * Given: 系統已成功爬取並顯示留言資料表格
   * When: 使用者點擊某一列的「客戶確認/修改處」欄位並輸入文字
   * Then: 該欄位立即更新為使用者輸入的內容
   */
  it('驗收情境 2 (延伸): 使用者編輯客戶確認欄位,欄位立即更新', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 找到第三列的「客戶確認/修改處」輸入框
    const customerNotesInputs = screen.getAllByPlaceholderText('輸入備註');
    expect(customerNotesInputs.length).toBe(3);

    const thirdCustomerNotesInput = customerNotesInputs[2] as HTMLTextAreaElement;
    
    // 輸入文字
    await user.clear(thirdCustomerNotesInput);
    await user.type(thirdCustomerNotesInput, '客戶要求優先處理');

    // Assert - 驗證欄位更新
    await waitFor(() => {
      expect(thirdCustomerNotesInput.value).toBe('客戶要求優先處理');
    });

    // 驗證 store 中的資料已更新
    const updatedComments = useStore.getState().comments;
    expect(updatedComments[2].customer_notes).toBe('客戶要求優先處理');
  });

  /**
   * 驗收情境 3: 勾選並刪除留言
   * 
   * Given: 系統已成功爬取並顯示留言資料表格
   * When: 使用者勾選一或多列留言並點擊「刪除」按鈕
   * Then: 被勾選的列從表格中移除,剩餘資料重新排列
   */
  it('驗收情境 3: 使用者勾選並刪除留言,表格更新', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 找到留言的勾選框
    const checkboxes = screen.getAllByRole('checkbox');
    // 第一個是全選框,後面是各留言的勾選框
    expect(checkboxes.length).toBe(4); // 1 全選 + 3 留言

    // 勾選第一則和第三則留言
    await user.click(checkboxes[1]); // comment-1
    await user.click(checkboxes[3]); // comment-3

    // 確認選取狀態顯示
    await waitFor(() => {
      expect(screen.getByText(/已選取 2 \/ 3 則留言/i)).toBeInTheDocument();
    });

    // 找到刪除按鈕
    const deleteButton = screen.getByRole('button', { name: /刪除 2 則留言/i });
    expect(deleteButton).toBeInTheDocument();

    // Set up confirm to return true
    vi.mocked(window.confirm).mockReturnValue(true);

    // 點擊刪除
    await user.click(deleteButton);

    // Assert - 驗證確認對話框被呼叫
    expect(window.confirm).toHaveBeenCalledWith('確定要刪除 2 則留言嗎?此操作無法復原。');

    // 驗證表格更新
    await waitFor(() => {
      expect(screen.getByText('留言列表 (1 則)')).toBeInTheDocument();
    });

    // 驗證剩餘的是第二則留言
    const updatedComments = useStore.getState().comments;
    expect(updatedComments.length).toBe(1);
    expect(updatedComments[0].comment_id).toBe('comment-2');
    expect(updatedComments[0].commenter_id).toBe('Jane Smith (87654321)');

    // 確認第一則和第三則留言已被刪除
    expect(screen.queryByText('John Doe (12345678)')).not.toBeInTheDocument();
    expect(screen.queryByText('Bob Wilson (11111111)')).not.toBeInTheDocument();
    
    // 確認第二則留言仍存在
    expect(screen.getByText('Jane Smith (87654321)')).toBeInTheDocument();
  });

  /**
   * 驗收情境 3 (延伸): 取消刪除操作
   */
  it('驗收情境 3 (延伸): 使用者取消刪除,留言保留', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 勾選留言
    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[1]); // comment-1

    // Set up confirm to return false (取消)
    vi.mocked(window.confirm).mockReturnValue(false);

    // 點擊刪除
    const deleteButton = screen.getByRole('button', { name: /刪除 1 則留言/i });
    await user.click(deleteButton);

    // Assert - 驗證留言未被刪除
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    const comments = useStore.getState().comments;
    expect(comments.length).toBe(3);
  });

  /**
   * 驗收情境 3 (延伸): 全選並刪除所有留言
   */
  it('驗收情境 3 (延伸): 使用者全選並刪除所有留言', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 點擊全選框
    const checkboxes = screen.getAllByRole('checkbox');
    const selectAllCheckbox = checkboxes[0];
    await user.click(selectAllCheckbox);

    // 確認全選狀態
    await waitFor(() => {
      expect(screen.getByText(/已選取 3 \/ 3 則留言/i)).toBeInTheDocument();
    });

    // Set up confirm to return true
    vi.mocked(window.confirm).mockReturnValue(true);

    // 點擊刪除
    const deleteButton = screen.getByRole('button', { name: /刪除 3 則留言/i });
    await user.click(deleteButton);

    // Assert - 驗證所有留言被刪除,留言列表區塊消失
    await waitFor(() => {
      expect(screen.queryByText(/留言列表/i)).not.toBeInTheDocument();
    });

    const comments = useStore.getState().comments;
    expect(comments.length).toBe(0);
  });

  /**
   * 驗收情境 4: 重新整理頁面不保留編輯內容
   * 
   * Given: 使用者已編輯部分欄位
   * When: 使用者重新整理頁面或關閉瀏覽器後再次開啟
   * Then: 編輯內容不會保留,系統回到初始狀態
   * 
   * Note: 此測試驗證 store 的 reset 功能,實際的頁面重新整理行為由瀏覽器處理
   */
  it('驗收情境 4: Store reset 後編輯內容不保留', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 編輯第一則留言
    const replyWindowInputs = screen.getAllByPlaceholderText('輸入回覆窗口');
    const firstReplyWindowInput = replyWindowInputs[0] as HTMLInputElement;
    
    await user.clear(firstReplyWindowInput);
    await user.type(firstReplyWindowInput, '李經理');

    // 驗證編輯成功
    await waitFor(() => {
      expect(firstReplyWindowInput.value).toBe('李經理');
    });

    // 模擬頁面重新整理 (重置 store)
    const store = useStore.getState();
    store.reset();

    // Assert - 驗證資料已重置
    const resetComments = useStore.getState().comments;
    expect(resetComments.length).toBe(0);

    const resetPost = useStore.getState().post;
    expect(resetPost).toBeNull();
  });

  /**
   * 整合測試: 編輯後刪除
   */
  it('整合測試: 使用者編輯留言後刪除部分留言', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Act - 先編輯第一則留言
    const replyWindowInputs = screen.getAllByPlaceholderText('輸入回覆窗口');
    await user.clear(replyWindowInputs[0]);
    await user.type(replyWindowInputs[0], '王主管');

    const replyContentInputs = screen.getAllByPlaceholderText('輸入回覆內容');
    await user.clear(replyContentInputs[0]);
    await user.type(replyContentInputs[0], '感謝您的支持');

    // 驗證編輯成功
    await waitFor(() => {
      const comments = useStore.getState().comments;
      expect(comments[0].reply_window).toBe('王主管');
      expect(comments[0].reply_content).toBe('感謝您的支持');
    });

    // 再刪除第二則留言
    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[2]); // comment-2

    // Set up confirm to return true
    vi.mocked(window.confirm).mockReturnValue(true);

    const deleteButton = screen.getByRole('button', { name: /刪除 1 則留言/i });
    await user.click(deleteButton);

    // Assert - 驗證剩餘 2 則留言
    await waitFor(() => {
      expect(screen.getByText('留言列表 (2 則)')).toBeInTheDocument();
    });

    const finalComments = useStore.getState().comments;
    expect(finalComments.length).toBe(2);
    
    // 確認第一則留言的編輯內容保留
    expect(finalComments[0].reply_window).toBe('王主管');
    expect(finalComments[0].reply_content).toBe('感謝您的支持');
    
    // 確認第二則留言已刪除
    expect(finalComments.find(c => c.comment_id === 'comment-2')).toBeUndefined();
  });

  /**
   * 邊界情況: 無留言時不顯示刪除按鈕
   */
  it('邊界情況: 無留言時不顯示表格和刪除按鈕', async () => {
    // Arrange - 設置空的留言列表
    const store = useStore.getState();
    store.reset();
    store.setPost(mockPost);
    store.setComments([]);

    // Act
    render(<HomePage />);

    // Assert - 驗證不顯示留言列表區塊 (因為 comments.length === 0)
    expect(screen.queryByText(/留言列表/i)).not.toBeInTheDocument();

    // 驗證不顯示刪除按鈕
    expect(screen.queryByRole('button', { name: /刪除/i })).not.toBeInTheDocument();
    
    // 驗證顯示貼文資訊 (post 存在)
    expect(screen.getByText('貼文資訊')).toBeInTheDocument();
  });

  /**
   * 邊界情況: 未選取任何留言時不顯示刪除按鈕
   */
  it('邊界情況: 未選取留言時不顯示刪除按鈕', async () => {
    // Arrange
    render(<HomePage />);

    // 確認留言表格已顯示
    await waitFor(() => {
      expect(screen.getByText('留言列表 (3 則)')).toBeInTheDocument();
    });

    // Assert - 驗證不顯示刪除按鈕 (因為沒有選取任何留言)
    expect(screen.queryByRole('button', { name: /刪除/i })).not.toBeInTheDocument();

    // 驗證顯示選取狀態
    expect(screen.getByText(/已選取 0 \/ 3 則留言/i)).toBeInTheDocument();
  });
});
