import { describe, it, expect } from 'vitest'
import { apiUtils, ApiClientError } from '../../utils/api'

describe('apiUtils & ApiClientError (clean)', () => {
  it('creates ApiClientError with status and optional code/details', () => {
    const e = new ApiClientError('Boom', 418, 'I_AM_A_TEAPOT', 'short and stout')
    expect(e).toBeInstanceOf(Error)
    expect(e).toBeInstanceOf(ApiClientError)
    expect(e.message).toBe('Boom')
    expect(e.status).toBe(418)
    expect(e.code).toBe('I_AM_A_TEAPOT')
    expect(e.details).toBe('short and stout')
  })

  it('apiUtils.isApiError distinguishes custom errors', () => {
    const apiErr = new ApiClientError('Oops', 400)
    const plain = new Error('Oops')
    expect(apiUtils.isApiError(apiErr)).toBe(true)
    expect(apiUtils.isApiError(plain)).toBe(false)
  })

  it('getErrorMessage handles different inputs', () => {
    const apiErr = new ApiClientError('API fail', 500)
    expect(apiUtils.getErrorMessage(apiErr)).toBe('API fail')
    expect(apiUtils.getErrorMessage(new Error('Regular'))).toBe('Regular')
    expect(apiUtils.getErrorMessage('Stringy')).toBe('Stringy')
  })
})

// EOF
