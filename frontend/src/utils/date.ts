// Date utility functions for LifeTime AI application
// Matches backend logic in week_calculation.py

import type { AgeInfo } from '@/types'
import { WeekType } from '@/types'

/**
 * Constants used in date calculations
 */
export const DATE_CONSTANTS = {
  DAYS_PER_WEEK: 7,
  WEEKS_PER_YEAR: 52.1775, // More precise weeks per year
  MIN_YEAR: 1900,
  MAX_YEAR: new Date().getFullYear() + 100,
  DEFAULT_LIFESPAN: 80,
  DEFAULT_TIMEZONE: 'UTC',
} as const

/**
 * Date validation errors
 */
export class DateValidationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'DateValidationError'
  }
}

/**
 * Parse date string in various formats to Date object
 */
export function parseDate(dateStr: string): Date {
  // Handle ISO format (YYYY-MM-DD)
  const isoRegex = /^(\d{4})-(\d{2})-(\d{2})$/
  const isoMatch = isoRegex.exec(dateStr)
  if (isoMatch) {
    const [, year, month, day] = isoMatch
    const parsedYear = parseInt(year!)
    const parsedMonth = parseInt(month!)
    const parsedDay = parseInt(day!)

    // Validate ranges
    if (parsedMonth < 1 || parsedMonth > 12) {
      throw new DateValidationError(`Invalid month: ${parsedMonth}`)
    }
    if (parsedDay < 1 || parsedDay > 31) {
      throw new DateValidationError(`Invalid day: ${parsedDay}`)
    }

    const date = new Date(parsedYear, parsedMonth - 1, parsedDay)

    // Check if the date is valid (e.g., no February 30th)
    if (
      isNaN(date.getTime()) ||
      date.getFullYear() !== parsedYear ||
      date.getMonth() !== parsedMonth - 1 ||
      date.getDate() !== parsedDay
    ) {
      throw new DateValidationError(`Invalid date: ${dateStr}`)
    }

    return date
  }

  // Try parsing as regular date
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) {
    throw new DateValidationError(`Invalid date format: ${dateStr}`)
  }

  return date
}

/**
 * Format date to ISO string (YYYY-MM-DD)
 */
export function formatDateISO(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * Format date to localized string
 */
export function formatDateLocale(
  date: Date,
  locale = 'en-US',
  options?: Intl.DateTimeFormatOptions,
): string {
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options,
  }
  return date.toLocaleDateString(locale, defaultOptions)
}

/**
 * Validate date of birth
 */
export function validateDateOfBirth(date: Date): void {
  if (isNaN(date.getTime())) {
    throw new DateValidationError('Invalid date')
  }

  if (date > new Date()) {
    throw new DateValidationError('Date of birth cannot be in the future')
  }

  if (date.getFullYear() < DATE_CONSTANTS.MIN_YEAR) {
    throw new DateValidationError(`Date of birth must be after year ${DATE_CONSTANTS.MIN_YEAR}`)
  }
}

/**
 * Calculate the week number since birth (0-indexed)
 * Matches backend WeekCalculationService.calculate_current_week_index
 */
export function calculateWeeksSinceBirth(dateOfBirth: Date, targetDate: Date = new Date()): number {
  validateDateOfBirth(dateOfBirth)

  // Calculate difference in milliseconds
  const diffMs = targetDate.getTime() - dateOfBirth.getTime()

  // Convert to days and then to weeks
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const weekIndex = Math.floor(diffDays / DATE_CONSTANTS.DAYS_PER_WEEK)

  return Math.max(0, weekIndex)
}

/**
 * Calculate total weeks in lifespan
 * Matches backend WeekCalculationService.calculate_total_weeks
 */
export function calculateTotalLifetimeWeeks(
  lifespanYears: number = DATE_CONSTANTS.DEFAULT_LIFESPAN,
): number {
  if (lifespanYears <= 0 || lifespanYears > 150) {
    throw new DateValidationError('Lifespan must be between 1 and 150 years')
  }

  return Math.floor(lifespanYears * DATE_CONSTANTS.WEEKS_PER_YEAR)
}

/**
 * Calculate the start date of a specific week since birth
 */
export function calculateWeekStartDate(dateOfBirth: Date, weekIndex: number): Date {
  validateDateOfBirth(dateOfBirth)

  if (weekIndex < 0) {
    throw new DateValidationError('Week index must be non-negative')
  }

  const startDate = new Date(dateOfBirth)
  startDate.setDate(startDate.getDate() + weekIndex * DATE_CONSTANTS.DAYS_PER_WEEK)

  return startDate
}

/**
 * Calculate age information at a specific date
 */
export function calculateAge(dateOfBirth: Date, targetDate: Date = new Date()): AgeInfo {
  validateDateOfBirth(dateOfBirth)

  let years = targetDate.getFullYear() - dateOfBirth.getFullYear()
  let months = targetDate.getMonth() - dateOfBirth.getMonth()
  let days = targetDate.getDate() - dateOfBirth.getDate()

  // Adjust for negative days
  if (days < 0) {
    months--
    const lastMonth = new Date(targetDate.getFullYear(), targetDate.getMonth(), 0)
    days += lastMonth.getDate()
  }

  // Adjust for negative months
  if (months < 0) {
    years--
    months += 12
  }

  return {
    years: Math.max(0, years),
    months: Math.max(0, months),
    days: Math.max(0, days),
  }
}

/**
 * Determine week type (past, current, future)
 */
export function getWeekType(
  dateOfBirth: Date,
  weekIndex: number,
  referenceDate: Date = new Date(),
): WeekType {
  const currentWeekIndex = calculateWeeksSinceBirth(dateOfBirth, referenceDate)

  if (weekIndex < currentWeekIndex) {
    return WeekType.PAST
  } else if (weekIndex === currentWeekIndex) {
    return WeekType.CURRENT
  } else {
    return WeekType.FUTURE
  }
}

/**
 * Calculate days lived at the start of a specific week
 */
export function calculateDaysLived(dateOfBirth: Date, weekIndex: number): number {
  validateDateOfBirth(dateOfBirth)
  return weekIndex * DATE_CONSTANTS.DAYS_PER_WEEK
}

/**
 * Calculate life progress percentage
 */
export function calculateLifeProgress(
  dateOfBirth: Date,
  lifespanYears: number = DATE_CONSTANTS.DEFAULT_LIFESPAN,
  referenceDate: Date = new Date(),
): number {
  const currentWeek = calculateWeeksSinceBirth(dateOfBirth, referenceDate)
  const totalWeeks = calculateTotalLifetimeWeeks(lifespanYears)

  if (totalWeeks === 0) return 0

  const progress = (currentWeek / totalWeeks) * 100
  return Math.min(100, Math.max(0, progress))
}

/**
 * Get week date range (start and end dates)
 */
export function getWeekDateRange(dateOfBirth: Date, weekIndex: number): { start: Date; end: Date } {
  const startDate = calculateWeekStartDate(dateOfBirth, weekIndex)
  const endDate = new Date(startDate)
  endDate.setDate(endDate.getDate() + DATE_CONSTANTS.DAYS_PER_WEEK - 1)

  return { start: startDate, end: endDate }
}

/**
 * Check if a date falls within a specific week
 */
export function isDateInWeek(dateOfBirth: Date, weekIndex: number, targetDate: Date): boolean {
  const { start, end } = getWeekDateRange(dateOfBirth, weekIndex)
  return targetDate >= start && targetDate <= end
}

/**
 * Get current week information
 */
export function getCurrentWeekInfo(dateOfBirth: Date, referenceDate: Date = new Date()) {
  const weekIndex = calculateWeeksSinceBirth(dateOfBirth, referenceDate)
  const { start, end } = getWeekDateRange(dateOfBirth, weekIndex)
  const age = calculateAge(dateOfBirth, referenceDate)
  const daysLived = calculateDaysLived(dateOfBirth, weekIndex)

  return {
    weekIndex,
    weekStart: start,
    weekEnd: end,
    age,
    daysLived,
    isCurrentWeek: true,
    weekType: WeekType.CURRENT,
  }
}

/**
 * Get week summary information
 */
export function getWeekSummary(
  dateOfBirth: Date,
  weekIndex: number,
  referenceDate: Date = new Date(),
) {
  const { start, end } = getWeekDateRange(dateOfBirth, weekIndex)
  const weekType = getWeekType(dateOfBirth, weekIndex, referenceDate)
  const age = calculateAge(dateOfBirth, start)
  const daysLived = calculateDaysLived(dateOfBirth, weekIndex)
  const isCurrentWeek = weekIndex === calculateWeeksSinceBirth(dateOfBirth, referenceDate)

  return {
    weekIndex,
    weekStart: start,
    weekEnd: end,
    weekType,
    ageYears: age.years,
    ageMonths: age.months,
    ageDays: age.days,
    daysLived,
    isCurrentWeek,
  }
}

/**
 * Validate week index against user's current week
 */
export function validateWeekIndex(
  dateOfBirth: Date,
  weekIndex: number,
  allowFuture: boolean = false,
  referenceDate: Date = new Date(),
): void {
  if (weekIndex < 0) {
    throw new DateValidationError('Week index must be non-negative')
  }

  if (!allowFuture) {
    const currentWeek = calculateWeeksSinceBirth(dateOfBirth, referenceDate)
    if (weekIndex > currentWeek) {
      throw new DateValidationError('Cannot access future weeks')
    }
  }
}

/**
 * Add/subtract weeks from a date
 */
export function addWeeks(date: Date, weeks: number): Date {
  const result = new Date(date)
  result.setDate(result.getDate() + weeks * DATE_CONSTANTS.DAYS_PER_WEEK)
  return result
}

/**
 * Add/subtract days from a date
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

/**
 * Check if two dates are the same day
 */
export function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  )
}

/**
 * Get relative time string (e.g., "2 days ago", "in 3 weeks")
 */
export function getRelativeTime(date: Date, referenceDate: Date = new Date()): string {
  const diffMs = date.getTime() - referenceDate.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffWeeks = Math.floor(diffDays / 7)

  if (Math.abs(diffDays) < 1) {
    return 'today'
  } else if (Math.abs(diffDays) === 1) {
    return diffDays > 0 ? 'tomorrow' : 'yesterday'
  } else if (Math.abs(diffWeeks) < 1) {
    return diffDays > 0 ? `in ${diffDays} days` : `${Math.abs(diffDays)} days ago`
  } else if (Math.abs(diffWeeks) === 1) {
    return diffWeeks > 0 ? 'next week' : 'last week'
  } else {
    return diffWeeks > 0 ? `in ${diffWeeks} weeks` : `${Math.abs(diffWeeks)} weeks ago`
  }
}

/**
 * Get date range for current month
 */
export function getCurrentMonthRange(referenceDate: Date = new Date()): { start: Date; end: Date } {
  const start = new Date(referenceDate.getFullYear(), referenceDate.getMonth(), 1)
  const end = new Date(referenceDate.getFullYear(), referenceDate.getMonth() + 1, 0)

  return { start, end }
}

/**
 * Get date range for current year
 */
export function getCurrentYearRange(referenceDate: Date = new Date()): { start: Date; end: Date } {
  const start = new Date(referenceDate.getFullYear(), 0, 1)
  const end = new Date(referenceDate.getFullYear(), 11, 31)

  return { start, end }
}

/**
 * Utility function to create date from components
 */
export function createDate(year: number, month: number, day: number): Date {
  // Validate ranges
  if (month < 1 || month > 12) {
    throw new DateValidationError(`Invalid month: ${month}`)
  }
  if (day < 1 || day > 31) {
    throw new DateValidationError(`Invalid day: ${day}`)
  }

  const date = new Date(year, month - 1, day) // month is 0-indexed in Date constructor

  // Check if the date is valid (e.g., no February 30th)
  if (
    isNaN(date.getTime()) ||
    date.getFullYear() !== year ||
    date.getMonth() !== month - 1 ||
    date.getDate() !== day
  ) {
    throw new DateValidationError(`Invalid date: ${year}-${month}-${day}`)
  }

  return date
}

/**
 * Export all date utilities as a default object
 */
export const dateUtils = {
  // Constants
  DATE_CONSTANTS,

  // Core functions
  parseDate,
  formatDateISO,
  formatDateLocale,

  // Validation
  validateDateOfBirth,
  validateWeekIndex,

  // Week calculations
  calculateWeeksSinceBirth,
  calculateTotalLifetimeWeeks,
  calculateWeekStartDate,
  getWeekDateRange,
  isDateInWeek,
  getCurrentWeekInfo,
  getWeekSummary,

  // Age and time calculations
  calculateAge,
  calculateDaysLived,
  calculateLifeProgress,

  // Week types and status
  getWeekType,

  // Date manipulation
  addWeeks,
  addDays,
  isSameDay,

  // Utility functions
  getRelativeTime,
  getCurrentMonthRange,
  getCurrentYearRange,
  createDate,
}

export default dateUtils
