# Coding Rules

## Workflow: Search → Reuse → Refactor → Create

Before writing code:

1. **Search** the repo for existing utilities, types, scanners, mappers
2. **Reuse** shared packages (`packages/database`, `packages/scanner-sdk`, `packages/config`)
3. **Refactor** if close match exists
4. **Create** only when nothing suitable exists

Never duplicate: utilities, hooks, services, repositories, API handlers, components, SQL, types.

## TypeScript

- Strict mode only — never `any`
- Prefer interfaces; composition over inheritance
- Dependency injection over globals
- Functions < 50 lines where practical
- One responsibility per function/class

## Naming

| Kind      | Convention             | Example                                |
| --------- | ---------------------- | -------------------------------------- |
| Variables | camelCase, descriptive | `jobScanner`, `userId`                 |
| Classes   | PascalCase             | `ScannerEngine`, `DashboardRepository` |
| Constants | SCREAMING_SNAKE        | `MAX_RETRY`, `DEFAULT_TIMEOUT`         |
| Files     | kebab or domain name   | `scanner_engine.py`, `client.ts`       |

## Modules

Every module requires: `README.md`, tests, `CHANGELOG.md` (packages).

## Error handling

Never empty `catch`. Always log, wrap meaningful errors, retry when recoverable.

## Configuration

No hardcoded URLs, API keys, timeouts, or retry counts. Use env + config packages.

## Folder rules

| Path        | Rule                                            |
| ----------- | ----------------------------------------------- |
| `apps/`     | Application entry points only                   |
| `packages/` | Shared libraries — no app imports               |
| `scanners/` | One folder per source; implement SDK contract   |
| `scraper/`  | Orchestration only — no source-specific parsing |
| `.ai/`      | Agent instructions — not runtime code           |

## Git commits

Conventional commits: `type(scope): summary`

Examples: `feat(scanner): add greenhouse plugin`, `fix(dashboard): supabase env inlining`
