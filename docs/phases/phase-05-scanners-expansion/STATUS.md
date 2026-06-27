# Phase 5 — Remaining Scanners (One by One)

```yaml
status: pending
started:
completed:
```

## Deliverables (add incrementally — one PR per scanner)

| Scanner              | Source              | Auth                 | Status           |
| -------------------- | ------------------- | -------------------- | ---------------- |
| Arbeitnow            | JSON API            | None                 | partial (legacy) |
| RemoteOK             | JSON API            | None                 | [ ]              |
| WeWorkRemotely       | RSS                 | None                 | [ ]              |
| Greenhouse           | JSON API            | None                 | Phase 4          |
| Lever                | JSON API            | OAuth/key in Secrets | [ ]              |
| Ashby                | TBD                 | TBD                  | [ ]              |
| Workday              | Aggregator fallback | N/A                  | [ ]              |
| Company career pages | Configured URLs     | None                 | [ ]              |

Each scanner PR must include:

- [ ] Implementation in `scanners/{name}/`
- [ ] Normalization to canonical job schema
- [ ] Deduplication keys (`source` + `external_id`)
- [ ] Unit tests with fixture JSON
- [ ] Health check entry in `scripts/scanner_health.py`
- [ ] README with rate limits and attribution notes

## Rules

- One scanner per PR for reviewability
- No scanner merged without tests
- Respect API TOS (RemoteOK attribution on dashboard)

## Quality gate

- [ ] All targeted scanners pass health checks
- [ ] Cron pipeline ingests from all enabled sources without duplicate explosion

## Next phase

→ [Phase 6: AI Pipeline](../phase-06-ai-pipeline/)
