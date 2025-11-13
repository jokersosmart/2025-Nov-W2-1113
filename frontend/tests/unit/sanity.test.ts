/**
 * Sanity test to verify frontend test infrastructure
 */
import * as React from 'react'

describe('Sanity Tests', () => {
  it('should have Node.js 18+', () => {
    const version = process.version
    const major = parseInt(version.slice(1).split('.')[0])
    expect(major).toBeGreaterThanOrEqual(18)
  })

  it('should import React', () => {
    expect(React).toBeDefined()
  })

  it('should perform basic math', () => {
    expect(1 + 1).toBe(2)
  })
})
