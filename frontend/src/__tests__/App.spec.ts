import { describe, it, expect } from 'vitest'
import { createRouter, createWebHistory } from 'vue-router'
import { mount } from '@vue/test-utils'
import App from '../App.vue'

// Mock router for testing
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/about', name: 'about', component: { template: '<div>About</div>' } }
  ]
})

describe('App', () => {
  it('renders navigation correctly', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })
    
    expect(wrapper.text()).toContain('LifeTime AI-First')
    expect(wrapper.find('nav').exists()).toBe(true)
    expect(wrapper.find('footer').exists()).toBe(true)
  })

  it('contains navigation links', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })
    
    const links = wrapper.findAll('a')
    expect(links.length).toBeGreaterThanOrEqual(2)
    
    const homeLink = links.find(link => link.text() === 'Home')
    const aboutLink = links.find(link => link.text() === 'About')
    
    expect(homeLink).toBeDefined()
    expect(aboutLink).toBeDefined()
  })

  it('has proper structure', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router]
      }
    })
    
    expect(wrapper.find('#app').exists()).toBe(true)
    expect(wrapper.find('header').exists()).toBe(true)
    expect(wrapper.find('main').exists()).toBe(true)
    expect(wrapper.find('footer').exists()).toBe(true)
  })
})
