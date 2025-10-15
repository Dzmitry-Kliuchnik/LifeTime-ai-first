import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useVirtualScrolling, useGridVirtualScrolling } from '@/composables/useVirtualScrolling'

// Clean minimal smoke tests after previous file corruption.

describe('virtualization composables (smoke)', () => {
  it('virtual scrolling basics', () => {
    let composableResult: any

    const TestComponent = defineComponent({
      setup() {
        composableResult = useVirtualScrolling({
          totalItems: 1000,
          itemHeight: 20,
          containerHeight: 400,
          overscan: 5,
        })
        return {}
      },
      template: '<div></div>',
    })

    mount(TestComponent)

    expect(composableResult.state.value.totalHeight).toBe(20000)
    expect(composableResult.state.value.visibleItems.length).toBeGreaterThan(0)
  })

  it('grid position basics', () => {
    let composableResult: any

    const TestComponent = defineComponent({
      setup() {
        composableResult = useGridVirtualScrolling({
          totalItems: 4160,
          itemHeight: 12,
          columns: 52,
          cellWidth: 12,
          containerHeight: 600,
          gap: 1,
        })
        return {}
      },
      template: '<div></div>',
    })

    mount(TestComponent)

    const pos = composableResult.getGridPosition(104)
    expect(pos.row).toBe(2)
    expect(pos.col).toBe(0)
  })
})
