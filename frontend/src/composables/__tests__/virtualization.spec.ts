import { describe, it, expect } from 'vitest'
import { useVirtualScrolling, useGridVirtualScrolling } from '@/composables/useVirtualScrolling'

// Clean minimal smoke tests after previous file corruption.

describe('virtualization composables (smoke)', () => {
  it('virtual scrolling basics', () => {
    const { state } = useVirtualScrolling({
      totalItems: 1000,
      itemHeight: 20,
      containerHeight: 400,
      overscan: 5,
    })
    expect(state.value.totalHeight).toBe(20000)
    expect(state.value.visibleItems.length).toBeGreaterThan(0)
  })

  it('grid position basics', () => {
    const { getGridPosition } = useGridVirtualScrolling({
      totalItems: 4160,
      itemHeight: 12,
      columns: 52,
      cellWidth: 12,
      containerHeight: 600,
      gap: 1,
    })
    const pos = getGridPosition(104)
    expect(pos.row).toBe(2)
    expect(pos.col).toBe(0)
  })
})
