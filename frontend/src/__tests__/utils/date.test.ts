// Date utility tests
import { describe, it, expect } from 'vitest'
import {
  calculateWeeksSinceBirth,
  calculateTotalLifetimeWeeks,
  parseDate,
  formatDateISO,
  addWeeks,
  addDays,
  isSameDay,
} from '../../utils/date'

describe('Date Utilities', () => {
  const testDate = new Date('2023-06-15')
  const birthDate = new Date('1990-01-01')

  describe('calculateWeeksSinceBirth', () => {
    it('should calculate weeks since birth date', () => {
      const result = calculateWeeksSinceBirth(birthDate, testDate)
      expect(typeof result).toBe('number')
      expect(result).toBeGreaterThan(1000) // Should be many weeks
    })

    it('should return 0 for same date', () => {
      const result = calculateWeeksSinceBirth(testDate, testDate)
      expect(result).toBe(0)
    })
  })

  describe('calculateTotalLifetimeWeeks', () => {
    it('should calculate total lifetime weeks', () => {
      const result = calculateTotalLifetimeWeeks(80)
      expect(typeof result).toBe('number')
      expect(result).toBeGreaterThan(4000) // About 4160 weeks
    })

    it('should use default lifespan', () => {
      const result = calculateTotalLifetimeWeeks()
      expect(typeof result).toBe('number')
      expect(result).toBeGreaterThan(4000)
    })
  })

  describe('parseDate', () => {
    it('should parse valid date strings', () => {
      const result = parseDate('2023-06-15')
      expect(result).toBeInstanceOf(Date)
      expect(result.getFullYear()).toBe(2023)
      expect(result.getMonth()).toBe(5) // June (0-indexed)
      expect(result.getDate()).toBe(15)
    })
  })

  describe('formatDateISO', () => {
    it('should format dates correctly', () => {
      const result = formatDateISO(testDate)
      expect(typeof result).toBe('string')
      expect(result).toMatch(/\d{4}-\d{2}-\d{2}/)
    })
  })

  describe('addWeeks', () => {
    it('should add weeks correctly', () => {
      const result = addWeeks(testDate, 2)
      expect(result.getTime()).toBe(testDate.getTime() + 2 * 7 * 24 * 60 * 60 * 1000)
    })

    it('should handle negative weeks', () => {
      const result = addWeeks(testDate, -1)
      expect(result.getTime()).toBe(testDate.getTime() - 7 * 24 * 60 * 60 * 1000)
    })
  })

  describe('addDays', () => {
    it('should add days correctly', () => {
      const result = addDays(testDate, 5)
      expect(result.getTime()).toBe(testDate.getTime() + 5 * 24 * 60 * 60 * 1000)
    })
  })

  describe('isSameDay', () => {
    it('should identify same days correctly', () => {
      const date1 = new Date('2023-06-15T10:00:00')
      const date2 = new Date('2023-06-15T15:00:00')
      expect(isSameDay(date1, date2)).toBe(true)
    })

    it('should identify different days correctly', () => {
      const date1 = new Date('2023-06-15')
      const date2 = new Date('2023-06-16')
      expect(isSameDay(date1, date2)).toBe(false)
    })
  })
})
