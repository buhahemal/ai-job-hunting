# Phase 4 — Scanner SDK + Job Sources

```yaml
status: complete
started: 2026-06-27
completed: 2026-06-27
```

## Deliverables

- [x] `packages/scanner_sdk/` — BaseScanner, registry, HTTP, normalize, config
- [x] Required methods: `discover_jobs()`, `normalize()`, `health_check()`
- [x] Eight production scanners (public APIs, no subscription):
  - Greenhouse, Lever, SmartRecruiters, Teamtailor, Workable
  - RemoteOK, We Work Remotely, Company career pages
- [x] Unit tests for normalize + registry
- [x] `scanners/README.md` and `.env.example`

## Quality gate

- [x] All scanners registered in `get_registered_scanners()`
- [x] Health check script covers registered scanners
- [x] Env-based scanners skip gracefully when unconfigured

## Next phase

→ [Phase 5: AI Processing](../phase-04-ai-processing/)
