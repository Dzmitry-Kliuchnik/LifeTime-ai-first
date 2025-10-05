// E2E tests for LifeTime AI-First application

describe('LifeTime AI-First App', () => {
  it('visits the app root url and shows correct title', () => {
    cy.visit('/')
    cy.contains('h1', 'LifeTime AI-First')
    cy.contains('a', 'Home')
    cy.contains('a', 'About')
  })

  it('can navigate to About page', () => {
    cy.visit('/')
    cy.contains('a', 'About').click()
    cy.url().should('include', '/about')
  })

  it('can navigate back to Home page', () => {
    cy.visit('/about')
    cy.contains('a', 'Home').click()
    cy.url().should('eq', Cypress.config().baseUrl + '/')
  })
})
