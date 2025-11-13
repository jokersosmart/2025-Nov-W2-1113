import { create } from 'zustand';
import type { Post } from '../types/post';
import type { Comment } from '../types/comment';

/**
 * Scraping progress state
 */
export interface ScrapeProgress {
  scrapeId: string;
  status: 'idle' | 'scraping' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0-100
  totalComments: number;
  scrapedComments: number;
  message: string;
}

/**
 * Application state interface
 */
interface AppState {
  // Data
  post: Post | null;
  comments: Comment[];
  
  // Scraping state
  scrapeProgress: ScrapeProgress | null;
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // Actions - Post
  setPost: (post: Post | null) => void;
  
  // Actions - Comments
  setComments: (comments: Comment[]) => void;
  addComment: (comment: Comment) => void;
  updateComment: (commentId: string, updates: Partial<Comment>) => void;
  deleteComment: (commentId: string) => void;
  deleteComments: (commentIds: string[]) => void;
  
  // Actions - Scraping
  setScrapeProgress: (progress: ScrapeProgress | null) => void;
  updateScrapeProgress: (updates: Partial<ScrapeProgress>) => void;
  
  // Actions - UI
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Actions - Reset
  reset: () => void;
}

/**
 * Initial state
 */
const initialState = {
  post: null,
  comments: [],
  scrapeProgress: null,
  isLoading: false,
  error: null,
};

/**
 * Zustand store for application state
 */
export const useStore = create<AppState>((set) => ({
  ...initialState,
  
  // Post actions
  setPost: (post) => set({ post }),
  
  // Comment actions
  setComments: (comments) => set({ comments }),
  
  addComment: (comment) => 
    set((state) => ({
      comments: [...state.comments, comment],
    })),
  
  updateComment: (commentId, updates) =>
    set((state) => ({
      comments: state.comments.map((comment) =>
        comment.comment_id === commentId
          ? { ...comment, ...updates }
          : comment
      ),
    })),
  
  deleteComment: (commentId) =>
    set((state) => ({
      comments: state.comments.filter(
        (comment) => comment.comment_id !== commentId
      ),
    })),
  
  deleteComments: (commentIds) =>
    set((state) => ({
      comments: state.comments.filter(
        (comment) => !commentIds.includes(comment.comment_id)
      ),
    })),
  
  // Scraping actions
  setScrapeProgress: (progress) => set({ scrapeProgress: progress }),
  
  updateScrapeProgress: (updates) =>
    set((state) => ({
      scrapeProgress: state.scrapeProgress
        ? { ...state.scrapeProgress, ...updates }
        : null,
    })),
  
  // UI actions
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  
  // Reset
  reset: () => set(initialState),
}));

/**
 * Selectors for efficient component subscriptions
 */
export const selectPost = (state: AppState) => state.post;
export const selectComments = (state: AppState) => state.comments;
export const selectScrapeProgress = (state: AppState) => state.scrapeProgress;
export const selectIsLoading = (state: AppState) => state.isLoading;
export const selectError = (state: AppState) => state.error;

/**
 * Computed selectors
 */
export const selectCommentCount = (state: AppState) => state.comments.length;
export const selectIsScraping = (state: AppState) => 
  state.scrapeProgress?.status === 'scraping';
export const selectHasError = (state: AppState) => state.error !== null;
