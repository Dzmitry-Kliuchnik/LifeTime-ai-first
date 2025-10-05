import { describe, it, expect } from 'vitest'
import { ApiClientError } from '../../utils/api'

describe('API Basic Tests', () => {
  it('should create ApiClientError', () => {
    const error = new ApiClientError('Test error')
    expect(error.message).toBe('Test error')
    expect(error.name).toBe('ApiClientError')
  })
})