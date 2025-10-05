import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '@/components/HelloWorld.vue'

describe('HelloWorld.vue', () => {
  it('renders properly with default props', () => {
    const wrapper = mount(HelloWorld)
    expect(wrapper.text()).toContain('Hello World')
    expect(wrapper.text()).toContain('Welcome to Vue 3 + TypeScript + Vite')
  })

  it('renders with custom props', () => {
    const title = 'Custom Title'
    const message = 'Custom Message'
    const wrapper = mount(HelloWorld, {
      props: { title, message }
    })
    expect(wrapper.text()).toContain(title)
    expect(wrapper.text()).toContain(message)
  })

  it('increments counter when button is clicked', async () => {
    const wrapper = mount(HelloWorld)
    const button = wrapper.find('button')
    
    expect(button.text()).toContain('Count: 0')
    await button.trigger('click')
    
    // Wait for the async operation to complete
    await new Promise(resolve => setTimeout(resolve, 600))
    expect(button.text()).toContain('Count: 1')
  })

  it('shows loading state when button is clicked', async () => {
    const wrapper = mount(HelloWorld)
    const button = wrapper.find('button')
    
    expect(button.text()).toContain('Click me!')
    button.trigger('click')
    
    // Check loading state immediately after click
    await wrapper.vm.$nextTick()
    expect(button.text()).toContain('Loading...')
    expect(button.element).toHaveProperty('disabled', true)
  })
})