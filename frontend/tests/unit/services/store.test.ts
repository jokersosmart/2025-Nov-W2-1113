import { describe, it, expect, beforeEach } from 'vitest';
import { useStore, type ScrapeProgress } from '../../../src/services/store';
import type { Post } from '../../../src/types/post';
import type { Comment } from '../../../src/types/comment';

describe('Zustand Store', () => {
  beforeEach(() => {
    // Reset store before each test
    useStore.getState().reset();
  });

  describe('Post Management', () => {
    it('should set post', () => {
      const post: Post = {
        platform: 'facebook',
        post_url: 'https://facebook.com/test/posts/123',
        post_time: '2025-01-01T00:00:00Z',
        post_content: 'Test post',
        likes_count: 10,
        comments_count: 5,
      };

      useStore.getState().setPost(post);

      expect(useStore.getState().post).toEqual(post);
    });

    it('should clear post', () => {
      const post: Post = {
        platform: 'facebook',
        post_url: 'https://facebook.com/test/posts/123',
        post_time: '2025-01-01T00:00:00Z',
        post_content: 'Test post',
        likes_count: 10,
        comments_count: 5,
      };

      useStore.getState().setPost(post);
      useStore.getState().setPost(null);

      expect(useStore.getState().post).toBeNull();
    });
  });

  describe('Comment Management', () => {
    const mockComment: Comment = {
      comment_id: 'test-uuid-1',
      post_url: 'https://facebook.com/test/posts/123',
      comment_time: '2025-01-01T01:00:00Z',
      commenter_id: 'user123',
      comment_content: 'Test comment',
    };

    it('should set comments', () => {
      const comments = [mockComment];

      useStore.getState().setComments(comments);

      expect(useStore.getState().comments).toEqual(comments);
    });

    it('should add comment', () => {
      useStore.getState().addComment(mockComment);

      expect(useStore.getState().comments).toHaveLength(1);
      expect(useStore.getState().comments[0]).toEqual(mockComment);
    });

    it('should update comment', () => {
      useStore.getState().setComments([mockComment]);
      useStore.getState().updateComment('test-uuid-1', {
        customer_notes: 'Updated note',
      });

      expect(useStore.getState().comments[0].customer_notes).toBe('Updated note');
    });

    it('should not update non-existent comment', () => {
      useStore.getState().setComments([mockComment]);
      useStore.getState().updateComment('non-existent-id', {
        customer_notes: 'Note',
      });

      expect(useStore.getState().comments).toHaveLength(1);
      expect(useStore.getState().comments[0]).toEqual(mockComment);
    });

    it('should delete comment', () => {
      useStore.getState().setComments([mockComment]);
      useStore.getState().deleteComment('test-uuid-1');

      expect(useStore.getState().comments).toHaveLength(0);
    });

    it('should delete multiple comments', () => {
      const comment2: Comment = {
        ...mockComment,
        comment_id: 'test-uuid-2',
      };
      const comment3: Comment = {
        ...mockComment,
        comment_id: 'test-uuid-3',
      };

      useStore.getState().setComments([mockComment, comment2, comment3]);
      useStore.getState().deleteComments(['test-uuid-1', 'test-uuid-3']);

      expect(useStore.getState().comments).toHaveLength(1);
      expect(useStore.getState().comments[0].comment_id).toBe('test-uuid-2');
    });
  });

  describe('Scraping Progress', () => {
    const mockProgress: ScrapeProgress = {
      scrapeId: 'scrape-123',
      status: 'scraping',
      progress: 50,
      totalComments: 100,
      scrapedComments: 50,
      message: 'Scraping in progress',
    };

    it('should set scrape progress', () => {
      useStore.getState().setScrapeProgress(mockProgress);

      expect(useStore.getState().scrapeProgress).toEqual(mockProgress);
    });

    it('should update scrape progress', () => {
      useStore.getState().setScrapeProgress(mockProgress);
      useStore.getState().updateScrapeProgress({
        progress: 75,
        scrapedComments: 75,
      });

      expect(useStore.getState().scrapeProgress?.progress).toBe(75);
      expect(useStore.getState().scrapeProgress?.scrapedComments).toBe(75);
      expect(useStore.getState().scrapeProgress?.totalComments).toBe(100);
    });

    it('should not update when no progress exists', () => {
      useStore.getState().updateScrapeProgress({ progress: 50 });

      expect(useStore.getState().scrapeProgress).toBeNull();
    });
  });

  describe('UI State', () => {
    it('should set loading state', () => {
      useStore.getState().setLoading(true);

      expect(useStore.getState().isLoading).toBe(true);
    });

    it('should set error state', () => {
      const error = 'Test error';

      useStore.getState().setError(error);

      expect(useStore.getState().error).toBe(error);
    });

    it('should clear error state', () => {
      useStore.getState().setError('Error');
      useStore.getState().setError(null);

      expect(useStore.getState().error).toBeNull();
    });
  });

  describe('Reset', () => {
    it('should reset all state', () => {
      const post: Post = {
        platform: 'facebook',
        post_url: 'https://facebook.com/test/posts/123',
        post_time: '2025-01-01T00:00:00Z',
        post_content: 'Test',
        likes_count: 10,
        comments_count: 5,
      };
      const comment: Comment = {
        comment_id: 'test-uuid',
        post_url: 'https://facebook.com/test/posts/123',
        comment_time: '2025-01-01T01:00:00Z',
        commenter_id: 'user123',
        comment_content: 'Test comment',
      };

      useStore.getState().setPost(post);
      useStore.getState().addComment(comment);
      useStore.getState().setLoading(true);
      useStore.getState().setError('Error');
      useStore.getState().reset();

      expect(useStore.getState().post).toBeNull();
      expect(useStore.getState().comments).toEqual([]);
      expect(useStore.getState().isLoading).toBe(false);
      expect(useStore.getState().error).toBeNull();
      expect(useStore.getState().scrapeProgress).toBeNull();
    });
  });

  describe('Selectors', () => {
    it('should compute comment count', () => {
      const comment: Comment = {
        comment_id: 'test-uuid',
        post_url: 'https://facebook.com/test/posts/123',
        comment_time: '2025-01-01T01:00:00Z',
        commenter_id: 'user123',
        comment_content: 'Test comment',
      };

      useStore.getState().setComments([comment, { ...comment, comment_id: 'test-uuid-2' }]);

      const count = useStore.getState().comments.length;
      expect(count).toBe(2);
    });
  });
});
