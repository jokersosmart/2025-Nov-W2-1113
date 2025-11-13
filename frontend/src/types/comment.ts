/**
 * Comment entity type definitions
 */

/**
 * Comment interface representing a first-level comment on a post
 */
export interface Comment {
  /**
   * Unique identifier for the comment (UUID v4)
   */
  comment_id: string

  /**
   * URL of the parent post
   */
  post_url: string

  /**
   * Timestamp when the comment was posted (ISO 8601)
   */
  comment_time: string

  /**
   * Commenter identification in format "Name (ID)"
   * e.g., "John Doe (12345678)" or "@jane_doe (87654321)"
   */
  commenter_id: string

  /**
   * Text content of the comment (max 5,000 characters)
   */
  comment_content: string

  /**
   * Reply window name (user-editable, max 100 characters)
   * Optional field for user to fill in
   */
  reply_window?: string | null

  /**
   * Reply content text (user-editable, max 1,000 characters)
   * Optional field for user to fill in
   */
  reply_content?: string | null

  /**
   * Customer notes/modifications (user-editable, max 500 characters)
   * Optional field for user to fill in
   */
  customer_notes?: string | null

  /**
   * AI-generated reply placeholder (future feature, max 1,000 characters)
   * Reserved for future expansion
   */
  generated_reply?: string | null
}

/**
 * Validate UUID format
 */
export function isValidUUID(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
  return uuidRegex.test(uuid)
}

/**
 * Type for editable comment fields only
 */
export type EditableCommentFields = Pick<
  Comment,
  'reply_window' | 'reply_content' | 'customer_notes'
>

/**
 * Type for read-only comment fields
 */
export type ReadOnlyCommentFields = Omit<
  Comment,
  'reply_window' | 'reply_content' | 'customer_notes' | 'generated_reply'
>
