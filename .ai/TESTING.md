# Testing

## Stack

| Layer    | Tool                            |
| -------- | ------------------------------- |
| Frontend | Vitest + jsdom                  |
| Python   | unittest                        |
| Coverage | Vitest v8 (target ≥ 90%)        |
| E2E      | Future — Playwright in Phase 11 |

## Commands

```bash
npm test                    # All unit tests
npm run test:coverage       # Frontend coverage report
PYTHONPATH=. python3 -m unittest discover -s packages/scanner-sdk/tests
PYTHONPATH=. python3 -m unittest discover -s scraper/tests
PYTHONPATH=. python3 -m unittest discover -s packages/database/tests
```

## Required tests

| Change type         | Tests required                     |
| ------------------- | ---------------------------------- |
| New public function | Unit test                          |
| Scanner plugin      | Discovery, normalize, health_check |
| Database mapper     | Round-trip row ↔ record            |
| API endpoint        | Integration test                   |
| UI component        | Render + interaction (Vitest)      |

## Rules

- No trivial tests that assert constants
- Mock external HTTP in scanner unit tests where possible
- Use `USE_JSON_STORE=true` for pipeline tests without Supabase
- Fail CI on test failure — no skipped required tests

## Coverage

Coverage ≥ 90% is the target. CI reports coverage; enforcement increases per phase.
