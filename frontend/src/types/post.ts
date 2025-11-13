/**
 * Post entity type definitions
 */

/**
 * Platform enum for social media platforms
 */
export type Platform = 'facebook' | 'instagram'

/**
 * Post interface representing a social media post
 */
export interface Post {
  /**
   * Platform where the post was published
   */
  platform: Platform

  /**
   * URL of the post
   */
  post_url: string

  /**
   * Timestamp when the post was published (ISO 8601)
   */
  post_time: string

  /**
   * Text content of the post (max 10,000 characters)
   */
  post_content: string

  /**
   * Number of likes on the post
   */
  likes_count: number

  /**
   * Total number of comments on the post
   */
  comments_count: number
}

/**
 * Type guard to check if a platform string is valid
 */
export function isPlatform(value: string): value is Platform {
  return value === 'facebook' || value === 'instagram'
}

/**
 * Validate that post_url matches the platform
 */
export function validatePostUrl(platform: Platform, url: string): boolean {
  if (platform === 'facebook') {
    return url.includes('facebook.com')
  }
  if (platform === 'instagram') {
    return url.includes('instagram.com')
  }
  return false
}
