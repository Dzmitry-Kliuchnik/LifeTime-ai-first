// Tests for date utility functions
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { 
  dateUtils,
  parseDate,
  formatDateISO,
  validateDateOfBirth,
  calculateWeeksSinceBirth,
  calculateTotalLifetimeWeeks,
  calculateAge,
  getWeekType,
  DateValidationError,
  DATE_CONSTANTS
} from '../../utils/date'
import { WeekType } from '../../types'
import { 
  setupTest, 
  cleanupTest, 
  createTestDate,
  testValidation 
} from '../test-utils'

describe('Date Utilities', () => {
  beforeEach(() => {
    setupTest()
  })

  afterEach(() => {
    cleanupTest()
  })

  describe('Date Parsing and Formatting', () => {
    it('should parse ISO date strings correctly', () => {
      const dateStr = '1990-01-15'
      const parsed = parseDate(dateStr)
      
      expect(parsed).toBeInstanceOf(Date)
      expect(parsed.getFullYear()).toBe(1990)
      expect(parsed.getMonth()).toBe(0) // 0-indexed
      expect(parsed.getDate()).toBe(15)
    })

    it('should throw error for invalid date strings', () => {
      expect(() => parseDate('invalid-date')).toThrow(DateValidationError)
      expect(() => parseDate('2023-13-01')).toThrow(DateValidationError)
      expect(() => parseDate('2023-02-30')).toThrow(DateValidationError)
    })

    it('should format dates to ISO string', () => {
      const date = createTestDate(2023, 12, 1)
      const formatted = formatDateISO(date)
      
      expect(formatted).toBe('2023-12-01')
      expect(testValidation.isISODate(formatted)).toBe(true)
    })

    it('should format dates with locale options', () => {
      const date = createTestDate(2023, 12, 1)
      const formatted = dateUtils.formatDateLocale(date, 'en-US')
      
      expect(formatted).toContain('December')
      expect(formatted).toContain('2023')
    })
  })

  describe('Date Validation', () => {
    it('should validate valid dates of birth', () => {
      const validDate = createTestDate(1990, 1, 15)
      
      expect(() => validateDateOfBirth(validDate)).not.toThrow()
    })

    it('should reject future dates', () => {
      const futureDate = new Date()
      futureDate.setFullYear(futureDate.getFullYear() + 1)
      
      expect(() => validateDateOfBirth(futureDate)).toThrow(DateValidationError)
      expect(() => validateDateOfBirth(futureDate)).toThrow('future')
    })

    it('should reject dates before minimum year', () => {
      const oldDate = createTestDate(1800, 1, 1)
      
      expect(() => validateDateOfBirth(oldDate)).toThrow(DateValidationError)
      expect(() => validateDateOfBirth(oldDate)).toThrow('1900')
    })

    it('should reject invalid dates', () => {
      const invalidDate = new Date('invalid')
      
      expect(() => validateDateOfBirth(invalidDate)).toThrow(DateValidationError)
    })
  })

  describe('Week Calculations', () => {
    it('should calculate weeks since birth correctly', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const targetDate = createTestDate(2020, 1, 15) // 2 weeks later
      
      const weeks = calculateWeeksSinceBirth(birthDate, targetDate)
      
      expect(weeks).toBe(2)
    })

    it('should handle same date (week 0)', () => {
      const date = createTestDate(2020, 1, 1)
      const weeks = calculateWeeksSinceBirth(date, date)
      
      expect(weeks).toBe(0)
    })

    it('should calculate total lifetime weeks', () => {
      const totalWeeks80 = calculateTotalLifetimeWeeks(80)
      const totalWeeks70 = calculateTotalLifetimeWeeks(70)
      
      expect(totalWeeks80).toBeGreaterThan(totalWeeks70)
      expect(totalWeeks80).toBe(Math.floor(80 * DATE_CONSTANTS.WEEKS_PER_YEAR))
    })

    it('should throw error for invalid lifespan', () => {
      expect(() => calculateTotalLifetimeWeeks(0)).toThrow(DateValidationError)
      expect(() => calculateTotalLifetimeWeeks(-10)).toThrow(DateValidationError)
      expect(() => calculateTotalLifetimeWeeks(200)).toThrow(DateValidationError)
    })

    it('should calculate week start date correctly', () => {
      const birthDate = createTestDate(2020, 1, 1) // Wednesday
      const weekStart = dateUtils.calculateWeekStartDate(birthDate, 1)
      
      // Week 1 should start 7 days after birth
      const expectedStart = createTestDate(2020, 1, 8)
      expect(weekStart.getTime()).toBe(expectedStart.getTime())
    })
  })

  describe('Age Calculations', () => {
    it('should calculate age correctly', () => {
      const birthDate = createTestDate(1990, 1, 15)
      const targetDate = createTestDate(2023, 12, 1)
      
      const age = calculateAge(birthDate, targetDate)
      
      expect(age.years).toBe(33)
      expect(age.months).toBe(10)
      expect(age.days).toBeGreaterThanOrEqual(16)
    })

    it('should handle birthday on target date', () => {
      const birthDate = createTestDate(1990, 1, 15)
      const birthdayDate = createTestDate(2023, 1, 15)
      
      const age = calculateAge(birthDate, birthdayDate)
      
      expect(age.years).toBe(33)
      expect(age.months).toBe(0)
      expect(age.days).toBe(0)
    })

    it('should handle age calculation with months rollover', () => {
      const birthDate = createTestDate(1990, 12, 31)
      const targetDate = createTestDate(1991, 1, 1)
      
      const age = calculateAge(birthDate, targetDate)
      
      expect(age.years).toBe(0)
      expect(age.months).toBe(0)
      expect(age.days).toBe(1)
    })
  })

  describe('Week Types', () => {
    it('should identify past weeks correctly', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const currentDate = createTestDate(2020, 3, 1) // 8+ weeks later
      
      const weekType = getWeekType(birthDate, 2, currentDate)
      
      expect(weekType).toBe(WeekType.PAST)
    })

    it('should identify current week correctly', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const currentDate = createTestDate(2020, 1, 15) // 2 weeks later
      
      const currentWeekIndex = calculateWeeksSinceBirth(birthDate, currentDate)
      const weekType = getWeekType(birthDate, currentWeekIndex, currentDate)
      
      expect(weekType).toBe(WeekType.CURRENT)
    })

    it('should identify future weeks correctly', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const currentDate = createTestDate(2020, 1, 15) // 2 weeks later
      
      const weekType = getWeekType(birthDate, 10, currentDate)
      
      expect(weekType).toBe(WeekType.FUTURE)
    })
  })

  describe('Date Range Utilities', () => {
    it('should get week date range correctly', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const range = dateUtils.getWeekDateRange(birthDate, 1)
      
      expect(range.start.getTime()).toBe(createTestDate(2020, 1, 8).getTime())
      expect(range.end.getTime()).toBe(createTestDate(2020, 1, 14).getTime())
    })

    it('should check if date is in week', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const testDate = createTestDate(2020, 1, 10)
      
      const isInWeek = dateUtils.isDateInWeek(birthDate, 1, testDate)
      
      expect(isInWeek).toBe(true)
    })

    it('should get current month range', () => {
      const testDate = createTestDate(2023, 6, 15)
      const range = dateUtils.getCurrentMonthRange(testDate)
      
      expect(range.start.getDate()).toBe(1)
      expect(range.start.getMonth()).toBe(5) // June (0-indexed)
      expect(range.end.getDate()).toBe(30) // June has 30 days
    })
  })

  describe('Life Progress Calculations', () => {
    it('should calculate life progress percentage', () => {
      const birthDate = createTestDate(1990, 1, 1)
      const currentDate = createTestDate(2030, 1, 1) // 40 years later
      
      const progress = dateUtils.calculateLifeProgress(birthDate, 80, currentDate)
      
      expect(progress).toBeCloseTo(50, 0) // Approximately 50% of 80-year lifespan
    })

    it('should not exceed 100% progress', () => {
      const birthDate = createTestDate(1990, 1, 1)
      const currentDate = createTestDate(2080, 1, 1) // 90 years later (more than lifespan)
      
      const progress = dateUtils.calculateLifeProgress(birthDate, 80, currentDate)
      
      expect(progress).toBe(100)
    })

    it('should not be negative', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const currentDate = createTestDate(2019, 1, 1) // Before birth (edge case)
      
      const progress = dateUtils.calculateLifeProgress(birthDate, 80, currentDate)
      
      expect(progress).toBeGreaterThanOrEqual(0)
    })
  })

  describe('Utility Functions', () => {
    it('should add weeks to date correctly', () => {
      const startDate = createTestDate(2020, 1, 1)
      const resultDate = dateUtils.addWeeks(startDate, 2)
      
      expect(resultDate.getTime()).toBe(createTestDate(2020, 1, 15).getTime())
    })

    it('should add days to date correctly', () => {
      const startDate = createTestDate(2020, 1, 1)
      const resultDate = dateUtils.addDays(startDate, 5)
      
      expect(resultDate.getTime()).toBe(createTestDate(2020, 1, 6).getTime())
    })

    it('should check if dates are same day', () => {
      const date1 = createTestDate(2020, 1, 15)
      const date2 = new Date(2020, 0, 15, 14, 30) // Same day, different time
      const date3 = createTestDate(2020, 1, 16)
      
      expect(dateUtils.isSameDay(date1, date2)).toBe(true)
      expect(dateUtils.isSameDay(date1, date3)).toBe(false)
    })

    it('should generate relative time strings', () => {
      const baseDate = createTestDate(2020, 1, 15)
      
      expect(dateUtils.getRelativeTime(baseDate, baseDate)).toBe('today')
      expect(dateUtils.getRelativeTime(
        createTestDate(2020, 1, 16), 
        baseDate
      )).toBe('tomorrow')
      expect(dateUtils.getRelativeTime(
        createTestDate(2020, 1, 14), 
        baseDate
      )).toBe('yesterday')
    })
  })

  describe('Week Validation', () => {
    it('should validate week indices correctly', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const currentDate = createTestDate(2020, 3, 1) // 8+ weeks later
      
      expect(() => dateUtils.validateWeekIndex(birthDate, 5, false, currentDate)).not.toThrow()
      expect(() => dateUtils.validateWeekIndex(birthDate, -1, false, currentDate)).toThrow()
      expect(() => dateUtils.validateWeekIndex(birthDate, 20, false, currentDate)).toThrow()
    })

    it('should allow future weeks when specified', () => {
      const birthDate = createTestDate(2020, 1, 1)
      const currentDate = createTestDate(2020, 3, 1)
      
      expect(() => dateUtils.validateWeekIndex(birthDate, 20, true, currentDate)).not.toThrow()
    })
  })

  describe('Date Creation and Validation', () => {
    it('should create dates from components', () => {
      const date = dateUtils.createDate(2023, 12, 25)
      
      expect(date.getFullYear()).toBe(2023)
      expect(date.getMonth()).toBe(11) // December (0-indexed)
      expect(date.getDate()).toBe(25)
    })

    it('should throw error for invalid date components', () => {
      expect(() => dateUtils.createDate(2023, 13, 1)).toThrow(DateValidationError)
      expect(() => dateUtils.createDate(2023, 2, 30)).toThrow(DateValidationError)
    })
  })

  describe('Constants and Configuration', () => {
    it('should have correct constants', () => {
      expect(DATE_CONSTANTS.DAYS_PER_WEEK).toBe(7)
      expect(DATE_CONSTANTS.WEEKS_PER_YEAR).toBeCloseTo(52.1775, 4)
      expect(DATE_CONSTANTS.MIN_YEAR).toBe(1900)
      expect(DATE_CONSTANTS.DEFAULT_LIFESPAN).toBe(80)
      expect(DATE_CONSTANTS.DEFAULT_TIMEZONE).toBe('UTC')
    })
  })
})