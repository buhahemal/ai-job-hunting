# Security

## OWASP priorities

| Risk                    | Mitigation                                             |
| ----------------------- | ------------------------------------------------------ |
| Injection               | Parameterized Supabase queries; validate scanner input |
| Broken auth             | Service role server-side only; anon + RLS on frontend  |
| Sensitive data exposure | Never log secrets; no service key in Vite bundle       |
| SSRF                    | Scanners use allowlisted public APIs only              |
| XSS                     | React escaping; sanitize HTML in job descriptions      |
| CSRF                    | Supabase anon key + RLS; no cookie auth yet            |

## Secrets

| Secret                   | Where                        | Never                 |
| ------------------------ | ---------------------------- | --------------------- |
| `SUPABASE_SERVICE_KEY`   | GitHub Actions, local `.env` | Frontend, commits     |
| `SUPABASE_ANON_KEY`      | GitHub Pages build, frontend | Untrusted without RLS |
| `GREENHOUSE_BOARD_TOKEN` | GitHub Actions env           | Commits               |

Scan: Gitleaks on every PR.

## Rate limiting

- Scanner HTTP: 10s timeout, User-Agent header
- GitHub Actions cron: once daily (configurable)
- Supabase: respect free tier limits

## Dependency security

- CodeQL (JavaScript + Python)
- Dependency Review on PRs
- Renovate for automated updates
- Semgrep custom rules

## Input validation

- Canonical job schema enforced in `packages/scanner-sdk/python/normalize.py`
- Profile normalization in `apps/api/defaults.py`
- TypeScript strict types from `@ai-job-hunter/database`
