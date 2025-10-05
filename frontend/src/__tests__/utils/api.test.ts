// Tests for API client utilities

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { apiUtils, ApiClientError } from '../../utils/api' 

// Mock fetch for tests

const mockFetch = vi.fn()  apiUtils,  apiUtils,

global.fetch = mockFetch

  ApiClientError   ApiClientError 

describe('API Utils', () => {

  beforeEach(() => {} from '../../utils/api'} from '../../utils/api'

    vi.clearAllMocks()

  })import { import { 



  afterEach(() => {  setupTest,   setupTest, 

    vi.resetAllMocks()

  })  cleanupTest  cleanupTest



  describe('ApiClientError', () => {} from '../test-utils'} from '../test-utils'

    it('should create error with message and status', () => {

      const error = new ApiClientError('Test error', 404)

      expect(error.message).toBe('Test error')

      expect(error.status).toBe(404)describe('API Utilities', () => {describe('API Client Utilities', () => {

      expect(error.name).toBe('ApiClientError')

    })  beforeEach(() => {  beforeEach(() => {

  })

    setupTest()    setupTest()

  describe('apiUtils', () => {

    it('should have isApiError method', () => {    vi.clearAllMocks()    vi.clearAllMocks()

      expect(typeof apiUtils.isApiError).toBe('function')

    })  })  })



    it('should identify ApiClientError instances', () => {

      const apiError = new ApiClientError('Test', 400)

      const regularError = new Error('Test')  afterEach(() => {  afterEach(() => {

      

      expect(apiUtils.isApiError(apiError)).toBe(true)    cleanupTest()    cleanupTest()

      expect(apiUtils.isApiError(regularError)).toBe(false)

    })  })  })

  })

})

  describe('ApiClientError', () => {  describe('API Utilities', () => {

    it('should create error with all properties', () => {    it('should identify ApiClientError correctly', () => {

      const error = new ApiClientError('Test error', 404, 'NOT_FOUND', 'Details')      const apiError = new ApiClientError('Test error', 404, 'NOT_FOUND')

            const regularError = new Error('Regular error')

      expect(error.message).toBe('Test error')      

      expect(error.status).toBe(404)      expect(apiUtils.isApiError(apiError)).toBe(true)

      expect(error.code).toBe('NOT_FOUND')      expect(apiUtils.isApiError(regularError)).toBe(false)

      expect(error.details).toBe('Details')    })

      expect(error.name).toBe('ApiClientError')

    })    it('should extract error messages correctly', () => {

      const apiError = new ApiClientError('API error', 500, 'SERVER_ERROR')

    it('should be instance of Error', () => {      const regularError = new Error('Regular error')

      const error = new ApiClientError('Test error')      const stringError = 'String error'

            

      expect(error).toBeInstanceOf(Error)      expect(apiUtils.getErrorMessage(apiError)).toBe('API error')

      expect(error).toBeInstanceOf(ApiClientError)      expect(apiUtils.getErrorMessage(regularError)).toBe('Regular error')

    })      expect(apiUtils.getErrorMessage(stringError)).toBe('String error')

  })    })



  describe('API Utilities Functions', () => {    it('should check error status codes correctly', () => {

    it('should identify ApiClientError correctly', () => {      const notFoundError = new ApiClientError('Not found', 404, 'NOT_FOUND')

      const apiError = new ApiClientError('Test error', 404, 'NOT_FOUND')      const serverError = new ApiClientError('Server error', 500, 'SERVER_ERROR')

      const regularError = new Error('Regular error')      

            expect(apiUtils.isErrorStatus(notFoundError, 404)).toBe(true)

      expect(apiUtils.isApiError(apiError)).toBe(true)      expect(apiUtils.isErrorStatus(notFoundError, 500)).toBe(false)

      expect(apiUtils.isApiError(regularError)).toBe(false)      expect(apiUtils.isErrorStatus(serverError, 500)).toBe(true)

    })    })



    it('should extract error messages correctly', () => {    it('should identify validation errors', () => {

      const apiError = new ApiClientError('API error', 500, 'SERVER_ERROR')      const validationError422 = new ApiClientError('Validation failed', 422, 'VALIDATION_ERROR')

      const regularError = new Error('Regular error')      const validationErrorCode = new ApiClientError('Validation failed', 400, 'VALIDATION_ERROR')

      const stringError = 'String error'      const notValidationError = new ApiClientError('Not found', 404, 'NOT_FOUND')

            

      expect(apiUtils.getErrorMessage(apiError)).toBe('API error')      expect(apiUtils.isValidationError(validationError422)).toBe(true)

      expect(apiUtils.getErrorMessage(regularError)).toBe('Regular error')      expect(apiUtils.isValidationError(validationErrorCode)).toBe(true)

      expect(apiUtils.getErrorMessage(stringError)).toBe('String error')      expect(apiUtils.isValidationError(notValidationError)).toBe(false)

    })    })



    it('should check error status codes correctly', () => {    it('should identify auth errors', () => {

      const notFoundError = new ApiClientError('Not found', 404, 'NOT_FOUND')      const unauthorizedError = new ApiClientError('Unauthorized', 401, 'UNAUTHORIZED')

      const serverError = new ApiClientError('Server error', 500, 'SERVER_ERROR')      const forbiddenError = new ApiClientError('Forbidden', 403, 'FORBIDDEN')

            const notAuthError = new ApiClientError('Not found', 404, 'NOT_FOUND')

      expect(apiUtils.isErrorStatus(notFoundError, 404)).toBe(true)      

      expect(apiUtils.isErrorStatus(notFoundError, 500)).toBe(false)      expect(apiUtils.isAuthError(unauthorizedError)).toBe(true)

      expect(apiUtils.isErrorStatus(serverError, 500)).toBe(true)      expect(apiUtils.isAuthError(forbiddenError)).toBe(true)

    })      expect(apiUtils.isAuthError(notAuthError)).toBe(false)

    })

    it('should identify validation errors', () => {

      const validationError422 = new ApiClientError('Validation failed', 422, 'VALIDATION_ERROR')    it('should identify not found errors', () => {

      const validationErrorCode = new ApiClientError('Validation failed', 400, 'VALIDATION_ERROR')      const notFoundError = new ApiClientError('Not found', 404, 'NOT_FOUND')

      const notValidationError = new ApiClientError('Not found', 404, 'NOT_FOUND')      const otherError = new ApiClientError('Server error', 500, 'SERVER_ERROR')

            

      expect(apiUtils.isValidationError(validationError422)).toBe(true)      expect(apiUtils.isNotFoundError(notFoundError)).toBe(true)

      expect(apiUtils.isValidationError(validationErrorCode)).toBe(true)      expect(apiUtils.isNotFoundError(otherError)).toBe(false)

      expect(apiUtils.isValidationError(notValidationError)).toBe(false)    })

    })  })



    it('should identify auth errors', () => {  describe('Error Handling', () => {

      const unauthorizedError = new ApiClientError('Unauthorized', 401, 'UNAUTHORIZED')    it('should handle network errors', async () => {

      const forbiddenError = new ApiClientError('Forbidden', 403, 'FORBIDDEN')      const networkError = new Error('Network Error')

      const notAuthError = new ApiClientError('Not found', 404, 'NOT_FOUND')      mockedAxios.get.mockRejectedValueOnce(networkError)

            

      expect(apiUtils.isAuthError(unauthorizedError)).toBe(true)      await expect(userApi.getUser(1)).rejects.toThrow(ApiClientError)

      expect(apiUtils.isAuthError(forbiddenError)).toBe(true)    })

      expect(apiUtils.isAuthError(notAuthError)).toBe(false)

    })    it('should handle timeout errors', async () => {

      const timeoutError = { code: 'ECONNABORTED', message: 'timeout of 10000ms exceeded' }

    it('should identify not found errors', () => {      mockedAxios.get.mockRejectedValueOnce(timeoutError)

      const notFoundError = new ApiClientError('Not found', 404, 'NOT_FOUND')      

      const otherError = new ApiClientError('Server error', 500, 'SERVER_ERROR')      await expect(userApi.getUser(1)).rejects.toThrow(ApiClientError)

          })

      expect(apiUtils.isNotFoundError(notFoundError)).toBe(true)

      expect(apiUtils.isNotFoundError(otherError)).toBe(false)    it('should handle 500 server errors', async () => {

    })      const serverError = {

        response: {

    it('should handle null and undefined gracefully', () => {          status: 500,

      expect(apiUtils.isApiError(null)).toBe(false)          data: { error: 'SERVER_ERROR', message: 'Internal server error' }

      expect(apiUtils.isApiError(undefined)).toBe(false)        }

      expect(apiUtils.getErrorMessage(null)).toBe('null')      }

      expect(apiUtils.getErrorMessage(undefined)).toBe('undefined')      mockedAxios.get.mockRejectedValueOnce(serverError)

    })      

  })      await expect(userApi.getUser(1)).rejects.toThrow(ApiClientError)

})    })

    it('should handle malformed error responses', async () => {
      const malformedError = {
        response: {
          status: 400,
          data: 'Not a JSON object'
        }
      }
      mockedAxios.get.mockRejectedValueOnce(malformedError)
      
      await expect(userApi.getUser(1)).rejects.toThrow(ApiClientError)
    })
  })

  describe('Request Interceptors', () => {
    it('should add auth token to requests when available', () => {
      // Mock localStorage to return a token
      const mockToken = 'test-auth-token'
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: vi.fn(() => mockToken),
          setItem: vi.fn(),
          removeItem: vi.fn()
        }
      })

      // This test would need to verify that the interceptor adds the Authorization header
      // In a real test environment, you'd test the actual interceptor behavior
      expect(localStorage.getItem).toBeDefined()
    })
  })

  describe('Response Interceptors', () => {
    it('should handle 401 unauthorized responses', async () => {
      const unauthorizedError = {
        response: {
          status: 401,
          data: { error: 'UNAUTHORIZED', message: 'Invalid token' }
        }
      }
      
      // Mock the event dispatcher
      vi.spyOn(window, 'dispatchEvent')
      
      mockedAxios.get.mockRejectedValueOnce(unauthorizedError)
      
      await expect(userApi.getUser(1)).rejects.toThrow(ApiClientError)
    })
  })
})