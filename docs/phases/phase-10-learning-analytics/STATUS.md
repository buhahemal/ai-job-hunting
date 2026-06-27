# Phase 10 — Learning Engine + Analytics

```yaml
status: pending
started:
completed:
```

## Deliverables

- [ ] Feedback loop: Applied / Rejected / Ignored / Interview / Offer → stored in Supabase
- [ ] Re-weight scoring features from outcomes (logistic regression or simple weight tuning)
- [ ] Analytics dashboard: funnel, source quality, skill demand trends
- [ ] Company/source performance metrics
- [ ] Export learning weights to config (no opaque black box)
- [ ] A/B comparison: heuristic vs embedding score effectiveness

## Rules (from R&D §8.2)

- Start with manual weight adjustments; automate only with auditable logic
- Never train on fabricated data
- Learning runs in GitHub Actions (batch) or on-demand workflow — not paid ML platforms

## Quality gate

- [ ] Documented learning algorithm in this folder
- [ ] Tests prove weights update when user marks jobs Applied/Rejected

## Next phase

→ [Phase 11: Production Hardening](../phase-11-production-hardening/)
