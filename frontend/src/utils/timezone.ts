// Timezone utilities for LifeTime AI application
// Provides timezone detection, conversion, and timezone-aware date calculations

import type { TimezoneInfo } from '@/types'
import { dateUtils } from './date'

/**
 * Timezone-related constants and common timezones
 */
export const TIMEZONE_CONSTANTS = {
  DEFAULT_TIMEZONE: 'UTC',
  FALLBACK_TIMEZONE: 'UTC',
} as const

export const COMMON_TIMEZONES = [
  // UTC
  { name: 'UTC', label: 'UTC', offset: 0 },

  // North America
  { name: 'America/New_York', label: 'Eastern Time (ET)', offset: -5 },
  { name: 'America/Chicago', label: 'Central Time (CT)', offset: -6 },
  { name: 'America/Denver', label: 'Mountain Time (MT)', offset: -7 },
  { name: 'America/Los_Angeles', label: 'Pacific Time (PT)', offset: -8 },
  { name: 'America/Phoenix', label: 'Arizona Time', offset: -7 },
  { name: 'America/Toronto', label: 'Toronto', offset: -5 },
  { name: 'America/Vancouver', label: 'Vancouver', offset: -8 },

  // Europe
  { name: 'Europe/London', label: 'London (GMT/BST)', offset: 0 },
  { name: 'Europe/Paris', label: 'Paris (CET/CEST)', offset: 1 },
  { name: 'Europe/Berlin', label: 'Berlin (CET/CEST)', offset: 1 },
  { name: 'Europe/Rome', label: 'Rome (CET/CEST)', offset: 1 },
  { name: 'Europe/Madrid', label: 'Madrid (CET/CEST)', offset: 1 },
  { name: 'Europe/Amsterdam', label: 'Amsterdam (CET/CEST)', offset: 1 },
  { name: 'Europe/Moscow', label: 'Moscow (MSK)', offset: 3 },

  // Asia
  { name: 'Asia/Tokyo', label: 'Tokyo (JST)', offset: 9 },
  { name: 'Asia/Shanghai', label: 'Shanghai (CST)', offset: 8 },
  { name: 'Asia/Seoul', label: 'Seoul (KST)', offset: 9 },
  { name: 'Asia/Kolkata', label: 'Mumbai/Delhi (IST)', offset: 5.5 },
  { name: 'Asia/Dubai', label: 'Dubai (GST)', offset: 4 },
  { name: 'Asia/Singapore', label: 'Singapore (SGT)', offset: 8 },
  { name: 'Asia/Hong_Kong', label: 'Hong Kong (HKT)', offset: 8 },

  // Australia/Pacific
  { name: 'Australia/Sydney', label: 'Sydney (AEST/AEDT)', offset: 10 },
  { name: 'Australia/Melbourne', label: 'Melbourne (AEST/AEDT)', offset: 10 },
  { name: 'Australia/Perth', label: 'Perth (AWST)', offset: 8 },
  { name: 'Pacific/Auckland', label: 'Auckland (NZST/NZDT)', offset: 12 },

  // South America
  { name: 'America/Sao_Paulo', label: 'São Paulo (BRT)', offset: -3 },
  { name: 'America/Argentina/Buenos_Aires', label: 'Buenos Aires (ART)', offset: -3 },

  // Africa
  { name: 'Africa/Cairo', label: 'Cairo (EET)', offset: 2 },
  { name: 'Africa/Johannesburg', label: 'Johannesburg (SAST)', offset: 2 },
] as const

/**
 * Timezone validation error
 */
export class TimezoneError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'TimezoneError'
  }
}

/**
 * Detect user's current timezone
 */
export function detectUserTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || TIMEZONE_CONSTANTS.DEFAULT_TIMEZONE
  } catch {
    return TIMEZONE_CONSTANTS.DEFAULT_TIMEZONE
  }
}

/**
 * Validate timezone string
 */
export function validateTimezone(timezone: string): void {
  try {
    new Intl.DateTimeFormat('en-US', { timeZone: timezone })
  } catch {
    throw new TimezoneError(`Invalid timezone: ${timezone}`)
  }
}

/**
 * Get timezone information including offset and abbreviation
 */
export function getTimezoneInfo(timezone: string, date: Date = new Date()): TimezoneInfo {
  validateTimezone(timezone)

  try {
    const formatter = new Intl.DateTimeFormat('en-US', {
      timeZone: timezone,
      timeZoneName: 'short',
    })

    const parts = formatter.formatToParts(date)
    const timeZoneName = parts.find((part) => part.type === 'timeZoneName')?.value || ''

    // Calculate offset in hours
    const utcDate = new Date(date.toLocaleString('en-US', { timeZone: 'UTC' }))
    const timezoneDate = new Date(date.toLocaleString('en-US', { timeZone: timezone }))
    const offsetMs = timezoneDate.getTime() - utcDate.getTime()
    const offsetHours = offsetMs / (1000 * 60 * 60)

    return {
      name: timezone,
      offset: offsetHours,
      abbreviation: timeZoneName,
    }
  } catch (error) {
    throw new TimezoneError(
      `Failed to get timezone info: ${error instanceof Error ? error.message : String(error)}`,
    )
  }
}

/**
 * Convert date to specific timezone
 */
export function convertToTimezone(date: Date, timezone: string): Date {
  validateTimezone(timezone)

  try {
    const timeString = date.toLocaleString('en-CA', {
      timeZone: timezone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    })

    return new Date(timeString.replace(',', ''))
  } catch (error) {
    throw new TimezoneError(
      `Failed to convert to timezone: ${error instanceof Error ? error.message : String(error)}`,
    )
  }
}

/**
 * Get current date in specific timezone
 */
export function getCurrentDateInTimezone(timezone: string): Date {
  return convertToTimezone(new Date(), timezone)
}

/**
 * Format date in specific timezone
 */
export function formatDateInTimezone(
  date: Date,
  timezone: string,
  options: Intl.DateTimeFormatOptions = {},
): string {
  validateTimezone(timezone)

  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    timeZone: timezone,
    ...options,
  }

  return date.toLocaleDateString('en-US', defaultOptions)
}

/**
 * Get timezone-aware week calculations
 */
export function calculateWeeksSinceBirthInTimezone(
  dateOfBirth: Date,
  timezone: string,
  referenceDate?: Date,
): number {
  validateTimezone(timezone)

  const targetDate = referenceDate
    ? convertToTimezone(referenceDate, timezone)
    : getCurrentDateInTimezone(timezone)
  const birthInTimezone = convertToTimezone(dateOfBirth, timezone)

  return dateUtils.calculateWeeksSinceBirth(birthInTimezone, targetDate)
}

/**
 * Get current week info in specific timezone
 */
export function getCurrentWeekInfoInTimezone(dateOfBirth: Date, timezone: string) {
  validateTimezone(timezone)

  const currentDateInTz = getCurrentDateInTimezone(timezone)
  const birthInTz = convertToTimezone(dateOfBirth, timezone)

  return dateUtils.getCurrentWeekInfo(birthInTz, currentDateInTz)
}

/**
 * Get week summary in specific timezone
 */
export function getWeekSummaryInTimezone(dateOfBirth: Date, weekIndex: number, timezone: string) {
  validateTimezone(timezone)

  const currentDateInTz = getCurrentDateInTimezone(timezone)
  const birthInTz = convertToTimezone(dateOfBirth, timezone)

  return dateUtils.getWeekSummary(birthInTz, weekIndex, currentDateInTz)
}

/**
 * Get timezone offset string (e.g., '+05:30', '-08:00')
 */
export function getTimezoneOffsetString(timezone: string, date: Date = new Date()): string {
  validateTimezone(timezone)

  const info = getTimezoneInfo(timezone, date)
  const offset = info.offset

  if (offset === 0) {
    return '+00:00'
  }

  const sign = offset >= 0 ? '+' : '-'
  const absOffset = Math.abs(offset)
  const hours = Math.floor(absOffset)
  const minutes = Math.floor((absOffset - hours) * 60)

  return `${sign}${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}

/**
 * Get timezone label for display
 */
export function getTimezoneLabel(timezone: string): string {
  const found = COMMON_TIMEZONES.find((tz) => tz.name === timezone)
  if (found) {
    return found.label
  }

  return timezone.split('/').pop()?.replace(/_/g, ' ') || timezone
}

/**
 * Search timezones by name or location
 */
export function searchTimezones(query: string): (typeof COMMON_TIMEZONES)[number][] {
  const lowerQuery = query.toLowerCase()
  return COMMON_TIMEZONES.filter(
    (tz) =>
      tz.name.toLowerCase().includes(lowerQuery) || tz.label.toLowerCase().includes(lowerQuery),
  )
}

/**
 * Export all timezone utilities as a default object
 */
export const timezoneUtils = {
  TIMEZONE_CONSTANTS,
  COMMON_TIMEZONES,
  detectUserTimezone,
  validateTimezone,
  getTimezoneInfo,
  convertToTimezone,
  getCurrentDateInTimezone,
  formatDateInTimezone,
  calculateWeeksSinceBirthInTimezone,
  getCurrentWeekInfoInTimezone,
  getWeekSummaryInTimezone,
  getTimezoneOffsetString,
  getTimezoneLabel,
  searchTimezones,
}

export default timezoneUtils
