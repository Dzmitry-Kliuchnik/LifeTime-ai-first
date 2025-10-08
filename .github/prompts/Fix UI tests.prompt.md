- Objective
  - Run and fix UI tests for a Vue 3 + TypeScript app built with Vite, using Pinia for state, Vue Router 4 for routing, Axios for HTTP, Vitest for unit/component tests, and Cypress for e2e. Ensure ESLint and Prettier pass.

- Context
  - Framework: `Vue 3`, `TypeScript`, `Vite`
  - State: `Pinia`
  - Routing: `Vue Router 4`
  - HTTP: `Axios`
  - Tests: `Vitest` (unit/component), `Cypress` (e2e)
  - Code Quality: `ESLint`, `Prettier`

- What to Do
  - Discover and run all Vitest and Cypress tests.
  - Triage failures; identify whether the bug is in code, test, or configuration.
  - Implement minimal, correct fixes prioritizing user-visible behavior and test reliability.
  - Add or repair selectors using `data-test` attributes where needed to stabilize tests.
  - Mock integrations cleanly:
    - Axios: `vi.mock('axios')` with typed responses; use `flushPromises` after resolving.
    - Pinia: `createTestingPinia({ stubActions: true })` and inject into mounts.
    - Router: use `createRouter` + `createMemoryHistory` in tests; spy on `router.push`.
  - For Vue Test Utils, use `mount`/`shallowMount`, prefer async-friendly assertions and avoid brittle timing.
  - For Cypress, use `cy.intercept` instead of real network, avoid `cy.wait()` without a route alias.
  - Keep tests deterministic; avoid relying on timers; use `vi.useFakeTimers()` carefully.

- Execution Steps
  1) Run unit/component tests, collect failures, and coverage.
  2) Run e2e tests headless and interactive to reproduce.
  3) Fix root causes with minimal changes; update tests and mocks.
  4) Ensure lint and formatting pass; re-run all tests.
  5) Summarize changes, affected files, and rationale.

- Constraints
  - Do not introduce breaking API changes; maintain public component props/emit contracts.
  - Prefer adding `data-test="…"` for stable selectors over CSS structure-based queries.
  - No arbitrary sleeps; use `await nextTick()` / `flushPromises` and event-driven flows.
  - Keep router and store instances isolated per test; reset between tests.
  - Maintain TypeScript strictness; update types when behavior changes.
  - Ensure tests pass on clean install (`npm ci`).

- Output Required
  - Failing test list with error summaries.
  - Root cause analysis per failure and fix plan.
  - Patch-style diff for changed files and updated tests.
  - Notes on mocks/stubs added and why.
  - Post-fix test run results (Vitest + Cypress), coverage delta, and lint/format status.

- Troubleshooting Checklist
  - Async rendering: always `await nextTick()` and `await flushPromises()` after actions.
  - Pinia: verify store state setup via `setActivePinia(createPinia())` or testing pinia in mounts.
  - Router: when testing navigation guards, mount with `createMemoryHistory()`.
  - Axios: ensure mocked response shape matches production types; test error paths.
  - Cypress: drive via `data-test` selectors; use `cy.intercept` with fixtures; ensure app waits on network via route aliases.
  - Accessibility: prefer role-based selectors where practical; keep keyboard flows tested.

- Acceptance Criteria
  - All Vitest and Cypress tests pass consistently locally and in CI.
  - Lint (`ESLint`) and format (`Prettier`) pass with no warnings.
  - Coverage stable or improved for critical UI paths.
  - Changes documented with rationale and test evidence.

**Quick Commands (Windows)**
- Run Vitest (one-off, with coverage)
```bash
npx vitest run --coverage
```
- Run Vitest (watch mode)
```bash
npx vitest --watch
```
- Open Cypress (interactive)
```bash
npx cypress open
```
- Run Cypress (headless)
```bash
npx cypress run
```
- Lint
```bash
npx eslint . --ext .ts,.tsx,.vue
```
- Format
```bash
npx prettier -w .
```

Notes
- Use `data-test` attributes across components to stabilize both Vitest and Cypress selectors.
- Keep mocks co-located with tests or use shared helpers (e.g., `tests/helpers/mocks.ts`) for Axios/Pinia/Router.
- If you want, I can tailor this prompt further to your repo’s actual structure (e.g., exact test directories, config filenames).
        