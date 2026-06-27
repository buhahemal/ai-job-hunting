# Phase 11 — Performance, Security, Production Hardening

```yaml
status: pending
started:
completed:
```

## Deliverables

### Performance
- [ ] GitHub Actions minutes audit (stay within 2000 min/month public repo)
- [ ] Model quantization / smaller HF models if OOM on runner
- [ ] Supabase query indexes reviewed (EXPLAIN plans)
- [ ] Frontend bundle size budget

### Security
- [ ] Full OWASP review checklist
- [ ] Secret rotation documented
- [ ] RLS audit on all tables
- [ ] Dependency audit (CodeQL + dependabot)
- [ ] Gitleaks clean

### Production
- [ ] Runbooks: failed cron, Supabase outage, model download failure
- [ ] Monitoring: Actions failure notifications
- [ ] Backup: Supabase backup strategy (free tier limits documented)
- [ ] All phases 1–10 marked `done`
- [ ] Release tagged via `release.yml`

## Quality gate

- [ ] Security review passed
- [ ] Performance review passed
- [ ] Cost review: **₹0 confirmed**
- [ ] Production checklist signed off in this STATUS file

## Project complete when

All 11 phases are `done` and dashboard is live on GitHub Pages with automated pipeline on GitHub Actions.
