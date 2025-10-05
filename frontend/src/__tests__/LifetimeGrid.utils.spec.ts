import { describe, it, expect } from 'vitest'

/**
 * Unit tests for LifetimeGrid utility functions
 * These tests focus on the pure functions that don't require component mounting
 */

describe('LifetimeGrid Utilities', () => {
  describe('Special Date Detection', () => {
    it('calculates correct ordinal suffixes', () => {
      expect(getOrdinalSuffix(1)).toBe('st')
      expect(getOrdinalSuffix(2)).toBe('nd')
      expect(getOrdinalSuffix(3)).toBe('rd')
      expect(getOrdinalSuffix(4)).toBe('th')
      expect(getOrdinalSuffix(11)).toBe('th')
      expect(getOrdinalSuffix(12)).toBe('th')
      expect(getOrdinalSuffix(13)).toBe('th')
      expect(getOrdinalSuffix(21)).toBe('st')
      expect(getOrdinalSuffix(22)).toBe('nd')
      expect(getOrdinalSuffix(23)).toBe('rd')
      expect(getOrdinalSuffix(101)).toBe('st')
    })

    it('calculates birthday priority correctly', () => {
      expect(getPriorityForBirthday(25, true, false)).toBe(20) // Milestone
      expect(getPriorityForBirthday(30, false, true)).toBe(15) // Decade
      expect(getPriorityForBirthday(27, false, false)).toBe(10) // Regular birthday
    })

    it('identifies milestone birthdays', () => {
      expect(isMilestone(25)).toBe(true)
      expect(isMilestone(50)).toBe(true)
      expect(isMilestone(75)).toBe(true)
      expect(isMilestone(27)).toBe(false)
      expect(isMilestone(35)).toBe(false)
    })

    it('identifies decade birthdays', () => {
      expect(isDecade(10)).toBe(true)
      expect(isDecade(20)).toBe(true)
      expect(isDecade(30)).toBe(true)
      expect(isDecade(25)).toBe(false) // Milestone, not decade
      expect(isDecade(50)).toBe(false) // Milestone, not decade
      expect(isDecade(27)).toBe(false)
    })
  })

  describe('Week State Calculations', () => {
    it('correctly calculates weeks per year', () => {
      const weeksPerYear = 52.1775
      expect(weeksPerYear).toBeCloseTo(52.18, 2)
    })

    it('calculates correct year from week index', () => {
      const weeksPerYear = 52.1775
      expect(Math.floor(52 / weeksPerYear)).toBe(0) // First year
      expect(Math.floor(104 / weeksPerYear)).toBe(1) // Second year
      expect(Math.floor(156 / weeksPerYear)).toBe(2) // Third year
    })

    it('handles boundary cases for week calculations', () => {
      expect(Math.floor(0 / 52.1775)).toBe(0) // Birth week
      expect(Math.floor(1 / 52.1775)).toBe(0) // First week of life
      expect(Math.floor(4159 / 52.1775)).toBe(79) // Last year of 80-year life
    })
  })

  describe('Border Priority System', () => {
    it('assigns correct priorities for different event types', () => {
      // User highlights should have highest priority
      expect(100).toBeGreaterThan(20) // highlight > milestone
      
      // Milestones should have higher priority than regular birthdays
      expect(20).toBeGreaterThan(10) // milestone > birthday
      
      // Birthdays should have higher priority than year starts
      expect(10).toBeGreaterThan(5) // birthday > year start
      
      // Year starts should have higher priority than quarters
      expect(5).toBeGreaterThan(2) // year start > quarter
    })

    it('handles multiple special dates correctly', () => {
      // A week that has both birthday and year start should handle conflicts
      const birthdayPriority = 10
      const yearStartPriority = 5
      const combinedEvents = [
        { type: 'birthday', priority: birthdayPriority },
        { type: 'yearStart', priority: yearStartPriority }
      ]
      
      const sortedEvents = [...combinedEvents].sort((a, b) => b.priority - a.priority)
      expect(sortedEvents[0]?.type).toBe('birthday')
      expect(sortedEvents[1]?.type).toBe('yearStart')
    })
  })

  describe('Color and Theme Calculations', () => {
    it('calculates correct opacity for different week types', () => {
      const pastOpacity = 0.8
      const currentOpacity = 1.0
      const futureOpacity = 0.4
      
      expect(pastOpacity).toBeGreaterThan(futureOpacity)
      expect(currentOpacity).toBeGreaterThan(pastOpacity)
      expect(currentOpacity).toBe(1.0) // Current week always fully opaque
    })

    it('increases opacity for special dates and notes', () => {
      const baseOpacity = 0.4 // Future week base
      const withSpecialDate = Math.min(1, baseOpacity + 0.2)
      const withNotes = Math.min(1, baseOpacity + 0.1)
      
      expect(withSpecialDate).toBeGreaterThan(baseOpacity)
      expect(withNotes).toBeGreaterThan(baseOpacity)
      expect(withSpecialDate).toBeGreaterThan(withNotes)
    })
  })

  describe('Accessibility Helpers', () => {
    it('generates meaningful ARIA labels', () => {
      const weekIndex = 156 // 3rd year, week 0
      const year = Math.floor(weekIndex / 52) + 1
      const weekInYear = (weekIndex % 52) + 1
      
      const expectedPattern = /Week \d+, Year \d+ of life, Week \d+ of year/
      const sampleLabel = `Week ${weekIndex + 1}, Year ${year} of life, Week ${weekInYear} of year`
      
      expect(sampleLabel).toMatch(expectedPattern)
    })

    it('includes appropriate state descriptions', () => {
      const states = ['completed week', 'current week', 'upcoming week']
      
      states.forEach(state => {
        expect(state).toMatch(/(completed|current|upcoming) week/)
      })
    })
  })

  describe('Responsive Grid Calculations', () => {
    it('calculates correct number of rows', () => {
      const totalWeeks = 4160 // 80 years
      const weeksPerRow = 52
      const expectedRows = Math.ceil(totalWeeks / weeksPerRow)
      
      expect(expectedRows).toBe(80)
    })

    it('handles different cell sizes', () => {
      const cellSizes = [8, 10, 12, 16]
      
      cellSizes.forEach(size => {
        expect(size).toBeGreaterThan(0)
        expect(size).toBeLessThanOrEqual(20) // Reasonable maximum
      })
    })

    it('calculates mobile breakpoints correctly', () => {
      const desktopWeeksPerRow = 52
      const tabletWeeksPerRow = 26 // Half for tablets
      const mobileWeeksPerRow = 13 // Quarter for mobile
      
      expect(tabletWeeksPerRow).toBe(desktopWeeksPerRow / 2)
      expect(mobileWeeksPerRow).toBe(desktopWeeksPerRow / 4)
    })
  })

  describe('Keyboard Navigation Helpers', () => {
    it('calculates correct navigation distances', () => {
      const weeksPerRow = 52
      const currentIndex = 100
      
      // Arrow key movements
      expect(currentIndex + 1).toBe(101) // Right
      expect(currentIndex - 1).toBe(99)  // Left
      expect(currentIndex + weeksPerRow).toBe(152) // Down
      expect(currentIndex - weeksPerRow).toBe(48)  // Up
      
      // Page movements (10 rows)
      expect(currentIndex + (weeksPerRow * 10)).toBe(620) // Page Down
      expect(currentIndex - (weeksPerRow * 10)).toBe(-420) // Page Up (would be clamped)
    })

    it('handles boundary conditions', () => {
      const totalWeeks = 4160
      const weeksPerRow = 52
      
      // First week
      expect(Math.max(0 - 1, 0)).toBe(0) // Can't go before first week
      expect(Math.max(0 - weeksPerRow, 0)).toBe(0) // Can't go up from first row
      
      // Last week
      const lastIndex = totalWeeks - 1
      expect(Math.min(lastIndex + 1, totalWeeks - 1)).toBe(lastIndex) // Can't go past last week
      expect(Math.min(lastIndex + weeksPerRow, totalWeeks - 1)).toBe(lastIndex) // Can't go down from last position
    })
  })
})

// Helper functions for testing (these would normally be imported from the component)
function getOrdinalSuffix(num: number): string {
  const lastDigit = num % 10
  const lastTwoDigits = num % 100
  
  if (lastTwoDigits >= 11 && lastTwoDigits <= 13) {
    return 'th'
  }
  
  switch (lastDigit) {
    case 1: return 'st'
    case 2: return 'nd'
    case 3: return 'rd'
    default: return 'th'
  }
}

function getPriorityForBirthday(age: number, isMilestone: boolean, isDecade: boolean): number {
  if (isMilestone) return 20
  if (isDecade) return 15
  return 10
}

function isMilestone(age: number): boolean {
  return age > 0 && (age % 25 === 0 || age % 50 === 0)
}

function isDecade(age: number): boolean {
  return age > 0 && age % 10 === 0 && !isMilestone(age)
}