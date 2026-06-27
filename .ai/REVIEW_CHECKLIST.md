# Review Checklist

Every PR and AI task must pass this checklist before merge.

## Architecture

- [ ] SOLID principles respected
- [ ] Clean separation: apps / packages / scanners / scraper
- [ ] No circular dependencies (`npm run arch:madge`)
- [ ] Packages do not import from apps (`npm run arch:depcruise`)
- [ ] Dependency direction correct (inward toward domain)

## Security

- [ ] No secrets committed (Gitleaks pass)
- [ ] Input validation on all external data
- [ ] Parameterized queries / Supabase client only
- [ ] RLS policies respected for anon key
- [ ] Semgrep pass

## Performance

- [ ] No N+1 query patterns
- [ ] Indexes used for filtered queries
- [ ] Pagination for large lists
- [ ] No unbounded memory growth in scanners

## Code quality

- [ ] Duplicate code < 3% (`npm run quality:duplicates`)
- [ ] No dead code (`npm run quality:dead-code`)
- [ ] ESLint + TypeScript strict pass
- [ ] No `console.log` in production paths
- [ ] No TODO comments left behind

## Testing

- [ ] Unit tests for new public functions
- [ ] Integration tests where boundaries change
- [ ] All tests pass (`npm test`)
- [ ] Coverage reported (target ≥ 90%)

## Documentation

- [ ] README updated for touched modules
- [ ] `.ai/` updated if agent rules change
- [ ] OpenAPI updated for API changes

## Cost

- [ ] ₹0 budget maintained — no paid services added
- [ ] Open-source alternatives preferred

## AI self-review questions

1. Production ready?
2. Can it be simplified?
3. Modular and scalable?
4. Edge cases handled?
5. Failures and retries handled?
6. Tests sufficient?
7. Operational cost unchanged?
