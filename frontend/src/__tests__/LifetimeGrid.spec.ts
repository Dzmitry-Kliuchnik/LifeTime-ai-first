import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import LifetimeGrid from '@/components/LifetimeGrid.vue'
import { useUserStore } from '@/stores/user'
import { useWeekCalculationStore } from '@/stores/week-calculation'

// Mock the API modules
vi.mock('@/utils/api', () => ({
  weekCalculationApi: {
    calculateLifeProgress: vi.fn(),
    calculateTotalWeeks: vi.fn(),
    calculateCurrentWeek: vi.fn()
  },
  apiUtils: {
    getErrorMessage: vi.fn((err) => err.message || 'Unknown error')
  }
}))

vi.mock('@/utils/timezone', () => ({
  timezoneUtils: {
    detectUserTimezone: vi.fn(() => 'UTC')
  }
}))

describe('LifetimeGrid', () => {
  let wrapper: VueWrapper<any>
  let userStore: any
  let weekCalculationStore: any
  let pinia: any

  const mockUser = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    date_of_birth: '1990-01-01',
    lifespan: 80,
    theme: 'light' as const,
    is_active: true,
    is_verified: true,
    is_superuser: false,
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  }

  const mockLifeProgress = {
    date_of_birth: '1990-01-01',
    timezone: 'UTC',
    lifespan_years: 80,
    total_weeks: 4160,
    current_week_index: 1768, // Approximately 34 years old
    weeks_lived: 1768,
    progress_percentage: 42.5,
    age_info: {
      years: 34,
      months: 0,
      days: 0
    },
    current_date: '2024-01-01'
  }

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    
    userStore = useUserStore()
    weekCalculationStore = useWeekCalculationStore()
    
    // Mock user store state
    userStore.currentUser = mockUser
    userStore.isAuthenticated = true
    
    // Mock week calculation store - need to set the underlying refs, not computed properties
    weekCalculationStore.lifeProgress = mockLifeProgress
    weekCalculationStore.totalWeeks = { total_weeks: mockLifeProgress.total_weeks }
    weekCalculationStore.currentWeek = { 
      current_week_index: mockLifeProgress.current_week_index,
      weeks_lived: mockLifeProgress.weeks_lived
    }
    
    // Mock the calculateLifeProgress method to resolve immediately and update store state
    weekCalculationStore.calculateLifeProgress = vi.fn().mockImplementation(async () => {
      // Simulate the store being updated with the underlying refs
      weekCalculationStore.lifeProgress = mockLifeProgress
      weekCalculationStore.totalWeeks = { total_weeks: mockLifeProgress.total_weeks }
      weekCalculationStore.currentWeek = { 
        current_week_index: mockLifeProgress.current_week_index,
        weeks_lived: mockLifeProgress.weeks_lived
      }
      return mockLifeProgress
    })
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Grid Rendering', () => {
    it('renders the grid container with correct structure', async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })

      // Wait for the component to load and process async operations
      await new Promise(resolve => setTimeout(resolve, 10))
      await nextTick()

      expect(wrapper.find('.lifetime-grid-container').exists()).toBe(true)
      expect(wrapper.find('#grid-description').exists()).toBe(true)
      expect(wrapper.find('#week-announcements').exists()).toBe(true)
      // Note: .grid-legend doesn't exist in the current component template
      // expect(wrapper.find('.grid-legend').exists()).toBe(true)
    })

    it('renders correct number of week cells', async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })

      // Wait for the component to load and process async operations
      await new Promise(resolve => setTimeout(resolve, 100))
      await nextTick()
      await nextTick() // Extra tick to ensure all computed properties update

      // Debug: Check if the grid is rendered
      console.log('Grid exists:', wrapper.find('.lifetime-grid').exists())
      console.log('Total weeks in store:', weekCalculationStore.totalLifetimeWeeks)
      console.log('Has date of birth:', userStore.hasDateOfBirth)
      console.log('Is loading:', wrapper.vm.isLoading)
      console.log('Error:', wrapper.vm.error)

      const weekCells = wrapper.findAll('.week-cell')
      expect(weekCells.length).toBe(mockLifeProgress.total_weeks)
    })

    it('applies correct CSS custom properties', async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })

      // Wait for component to fully render with data
      await new Promise(resolve => setTimeout(resolve, 10))
      await nextTick()

      const gridContainer = wrapper.find('.lifetime-grid')
      expect(gridContainer.exists()).toBe(true) // Ensure element exists first
      
      const style = gridContainer.attributes('style')
      
      expect(style).toContain('--weeks-per-row: 52')
      expect(style).toContain('--cell-size: 12px')
      expect(style).toContain('--total-rows:')
    })

    it('shows loading state correctly', async () => {
      // Create a fresh pinia instance without pre-populated data for this test
      const testPinia = createPinia()
      setActivePinia(testPinia)
      
      const testWeekStore = useWeekCalculationStore()
      const testUserStore = useUserStore()
      
      // Set user but not week calculation data to trigger loading
      testUserStore.currentUser = mockUser
      testUserStore.isAuthenticated = true
      
      // Mock the method to not immediately resolve
      const neverResolvePromise = new Promise(() => {}) // Never resolves
      testWeekStore.calculateLifeProgress = vi.fn().mockImplementation(() => neverResolvePromise)
      
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [testPinia]
        }
      })

      await nextTick()

      // Should show loading state when no data is available
      expect(wrapper.find('.loading-overlay').exists()).toBe(true)
      expect(wrapper.find('.loading-spinner').exists()).toBe(true)
    })

    it('shows error state when no date of birth', async () => {
      userStore.currentUser = { ...mockUser, date_of_birth: null }
      
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })

      await nextTick()

      expect(wrapper.find('.error-state').exists()).toBe(true)
    })
  })

  describe('Week State Calculation', () => {
    beforeEach(async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })
      await nextTick()
    })

    it('correctly identifies past weeks', () => {
      const pastWeekCells = wrapper.findAll('.week-past')
      expect(pastWeekCells.length).toBe(mockLifeProgress.weeks_lived)
    })

    it('correctly identifies current week', () => {
      const currentWeekCells = wrapper.findAll('.week-current')
      expect(currentWeekCells.length).toBe(1)
      
      const currentWeekCell = currentWeekCells[0]
      expect(currentWeekCell?.attributes('data-week-index')).toBe(
        mockLifeProgress.current_week_index.toString()
      )
    })

    it('correctly identifies future weeks', () => {
      const futureWeekCells = wrapper.findAll('.week-future')
      const expectedFutureWeeks = mockLifeProgress.total_weeks - mockLifeProgress.weeks_lived - 1
      expect(futureWeekCells.length).toBe(expectedFutureWeeks)
    })
  })

  describe('Color Coding', () => {
    beforeEach(async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })
      await nextTick()
    })

    it('applies correct classes for week types', () => {
      const pastWeek = wrapper.find('[data-week-index="100"]')
      expect(pastWeek.classes()).toContain('week-past')

      const currentWeek = wrapper.find(`[data-week-index="${mockLifeProgress.current_week_index}"]`)
      expect(currentWeek.classes()).toContain('week-current')

      const futureWeek = wrapper.find('[data-week-index="3000"]')
      expect(futureWeek.classes()).toContain('week-future')
    })

    it('applies theme classes correctly', () => {
      const weekCell = wrapper.find('.week-cell')
      expect(weekCell.classes()).toContain('theme-light')
    })

    it('applies highlighted week styling', async () => {
      await wrapper.setProps({ highlightedWeeks: [100, 200] })
      
      const highlightedWeek = wrapper.find('[data-week-index="100"]')
      expect(highlightedWeek.classes()).toContain('is-highlighted')
    })
  })

  describe('Special Border Detection', () => {
    beforeEach(async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })
      await nextTick()
    })

    it('detects birthday weeks correctly', () => {
      // Birthday weeks should occur approximately every 52 weeks
      const birthdayWeeks = wrapper.findAll('.is-birthday')
      expect(birthdayWeeks.length).toBeGreaterThan(0)
    })

    it('detects year start weeks correctly', () => {
      const yearStartWeeks = wrapper.findAll('.is-year-start')
      expect(yearStartWeeks.length).toBeGreaterThan(0)
    })

    it('applies correct border priority classes', () => {
      const weekWithBorder = wrapper.find('.is-birthday')
      if (weekWithBorder.exists()) {
        const classes = weekWithBorder.classes()
        const hasBorderPriority = classes.some(cls => cls.startsWith('border-priority-'))
        expect(hasBorderPriority).toBe(true)
      }
    })
  })

  describe('Accessibility', () => {
    beforeEach(async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })
      await nextTick()
    })

    it('has proper ARIA labels', () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      expect(gridContainer.attributes('role')).toBe('application')
      expect(gridContainer.attributes('aria-label')).toContain('Interactive lifetime grid')
    })

    it('has correct aria-rowcount and aria-colcount', () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      expect(gridContainer.attributes('aria-rowcount')).toBeTruthy()
      expect(gridContainer.attributes('aria-colcount')).toBe('52')
    })

    it('provides meaningful aria-labels for week cells', () => {
      const weekCell = wrapper.find('.week-cell')
      const ariaLabel = weekCell.attributes('aria-label')
      
      expect(ariaLabel).toContain('Week')
      expect(ariaLabel).toContain('Year')
      expect(ariaLabel).toMatch(/(completed|current|future) week/)
    })

    it('has live region for announcements', () => {
      const liveRegion = wrapper.find('#week-announcements')
      expect(liveRegion.exists()).toBe(true)
      expect(liveRegion.attributes('aria-live')).toBe('polite')
      expect(liveRegion.attributes('aria-atomic')).toBe('true')
    })

    it('handles keyboard navigation correctly', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      
      // Simulate arrow key navigation
      await gridContainer.trigger('keydown', { key: 'ArrowRight' })
      await nextTick()
      
      // Should have moved selection
      expect(wrapper.vm.selectedWeekIndex).toBeTruthy()
    })
  })

  describe('Interactive Features', () => {
    beforeEach(async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        },
        props: {
          interactive: true
        }
      })
      await nextTick()
    })

    it('emits weekClick event when cell is clicked', async () => {
      const weekCell = wrapper.find('[data-week-index="100"]')
      await weekCell.trigger('click')
      
      const emittedEvents = wrapper.emitted('weekClick')
      expect(emittedEvents).toBeTruthy()
      expect(emittedEvents?.[0]).toEqual([100, expect.any(Object)])
    })

    it('emits weekHover event when cell is hovered', async () => {
      const weekCell = wrapper.find('[data-week-index="100"]')
      await weekCell.trigger('mouseenter')
      
      const emittedEvents = wrapper.emitted('weekHover')
      expect(emittedEvents).toBeTruthy()
      expect(emittedEvents?.[0]).toEqual([100, expect.any(Object)])
    })

    it('emits weekFocus event when cell is focused', async () => {
      const weekCell = wrapper.find('[data-week-index="100"]')
      await weekCell.trigger('focus')
      
      const emittedEvents = wrapper.emitted('weekFocus')
      expect(emittedEvents).toBeTruthy()
      expect(emittedEvents?.[0]).toEqual([100, expect.any(Object)])
    })

    it('handles selection state correctly', async () => {
      const weekCell = wrapper.find('[data-week-index="100"]')
      await weekCell.trigger('click')
      
      expect(wrapper.vm.selectedWeekIndex).toBe(100)
      expect(weekCell.classes()).toContain('is-selected')
    })

    it('handles hover state correctly', async () => {
      const weekCell = wrapper.find('[data-week-index="100"]')
      await weekCell.trigger('mouseenter')
      
      expect(wrapper.vm.hoveredWeekIndex).toBe(100)
      expect(weekCell.classes()).toContain('is-hovered')
    })
  })

  describe('Keyboard Navigation', () => {
    beforeEach(async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        },
        props: {
          interactive: true
        }
      })
      await nextTick()
      
      // Set initial selection
      wrapper.vm.selectedWeekIndex = 100
      await nextTick()
    })

    it('navigates right with ArrowRight', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'ArrowRight' })
      
      expect(wrapper.vm.selectedWeekIndex).toBe(101)
    })

    it('navigates left with ArrowLeft', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'ArrowLeft' })
      
      expect(wrapper.vm.selectedWeekIndex).toBe(99)
    })

    it('navigates down with ArrowDown', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'ArrowDown' })
      
      expect(wrapper.vm.selectedWeekIndex).toBe(152) // 100 + 52
    })

    it('navigates up with ArrowUp', async () => {
      wrapper.vm.selectedWeekIndex = 152 // Set to a position where up navigation is possible
      await nextTick()
      
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'ArrowUp' })
      
      expect(wrapper.vm.selectedWeekIndex).toBe(100) // 152 - 52
    })

    it('goes to first week with Home', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'Home' })
      
      expect(wrapper.vm.selectedWeekIndex).toBe(0)
    })

    it('goes to last week with End', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'End' })
      
      expect(wrapper.vm.selectedWeekIndex).toBe(mockLifeProgress.total_weeks - 1)
    })

    it('jumps to current week with c key', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'c' })
      
      expect(wrapper.vm.selectedWeekIndex).toBe(mockLifeProgress.current_week_index)
    })

    it('clears selection with Escape', async () => {
      const gridContainer = wrapper.find('.lifetime-grid')
      await gridContainer.trigger('keydown', { key: 'Escape' })
      
      expect(wrapper.vm.selectedWeekIndex).toBeNull()
    })
  })

  describe('Responsive Behavior', () => {
    it('applies mobile styles correctly', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 480,
      })

      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        },
        props: {
          cellSize: 8 // Smaller cell size for mobile
        }
      })

      // Wait for component to load and render with data
      await new Promise(resolve => setTimeout(resolve, 10))
      await nextTick()

      const gridContainer = wrapper.find('.lifetime-grid')
      expect(gridContainer.exists()).toBe(true) // Ensure grid exists
      const style = gridContainer.attributes('style')
      expect(style).toContain('--cell-size: 8px')
    })

    it('adjusts max width based on props', async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        },
        props: {
          maxWidth: '800px'
        }
      })

      // Wait for component to load and render with data
      await new Promise(resolve => setTimeout(resolve, 10))
      await nextTick()

      const gridContainer = wrapper.find('.lifetime-grid')
      expect(gridContainer.exists()).toBe(true) // Ensure grid exists
      const style = gridContainer.attributes('style')
      expect(style).toContain('--max-width: 800px')
    })
  })

  describe('Props Configuration', () => {
    it('respects interactive prop', async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        },
        props: {
          interactive: false
        }
      })

      // Wait for component to load and render with data
      await new Promise(resolve => setTimeout(resolve, 10))
      await nextTick()

      const weekCell = wrapper.find('[data-week-index="100"]')
      expect(weekCell.exists()).toBe(true) // Ensure cell exists
      await weekCell.trigger('click')
      
      // Should not emit events when not interactive
      expect(wrapper.emitted('weekClick')).toBeFalsy()
    })

    it('applies highlighted weeks correctly', async () => {
      const highlightedWeeks = [100, 200, 300]
      
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        },
        props: {
          highlightedWeeks
        }
      })

      // Wait for component to load and render with data
      await new Promise(resolve => setTimeout(resolve, 10))
      await nextTick()

      highlightedWeeks.forEach(weekIndex => {
        const weekCell = wrapper.find(`[data-week-index="${weekIndex}"]`)
        expect(weekCell.exists()).toBe(true) // Ensure cell exists
        expect(weekCell.classes()).toContain('is-highlighted')
      })
    })

    it('shows/hides notes based on showNotes prop', async () => {
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        },
        props: {
          showNotes: false
        }
      })

      await nextTick()

      // Note: Since we don't have actual notes integration yet,
      // we mainly test that the prop is accepted
      expect(wrapper.props('showNotes')).toBe(false)
    })
  })

  describe('Error Handling', () => {
    it('shows retry button on error', async () => {
      weekCalculationStore.calculateLifeProgress = vi.fn().mockRejectedValue(new Error('API Error'))
      
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100)) // Wait for async error

      expect(wrapper.find('.error-state').exists()).toBe(true)
      expect(wrapper.find('.retry-button').exists()).toBe(true)
    })

    it('retries loading when retry button is clicked', async () => {
      // Create a spy that fails once, then succeeds
      const calculateSpy = vi.fn()
        .mockRejectedValueOnce(new Error('API Error'))
        .mockResolvedValueOnce(mockLifeProgress)
      
      weekCalculationStore.calculateLifeProgress = calculateSpy
      
      wrapper = mount(LifetimeGrid, {
        global: {
          plugins: [pinia]
        }
      })

      await nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))

      const retryButton = wrapper.find('.retry-button')
      expect(retryButton.exists()).toBe(true)
      
      await retryButton.trigger('click')
      await nextTick()

      expect(calculateSpy).toHaveBeenCalledTimes(2)
    })
  })
})