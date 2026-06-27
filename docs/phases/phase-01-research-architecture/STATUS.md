# Phase 1 — Research & Architecture

```yaml
status: done
started: 2026-06-27
completed: 2026-06-27
```

## Source documents

- [Deep Research Report](../../deep-research-report.md) — primary R&D specification
- [Executive Summary (PDF)](../../Executive%20Summary.pdf) — condensed vision
- [ARCHITECTURE.md](./ARCHITECTURE.md) — Phase 0 technical design (legacy, still valid)

## Deliverables

- [x] Objectives, scope, non-goals (₹0, no LinkedIn scrape)
- [x] Data source inventory (Arbeitnow, RemoteOK, WWR, Greenhouse, etc.)
- [x] Tool inventory (GitHub Actions, Supabase, Hugging Face)
- [x] Architecture & data flow diagrams
- [x] Supabase schema draft (jobs, resumes, applications, companies)
- [x] AI model selection (MiniLM, T5 resume, no paid APIs)
- [x] GitHub Actions pipeline design (~15 min cron)
- [x] Risk, compliance, and cost analysis

## Quality gate

- [x] Design-only phase — no production code required
- [x] All decisions documented and linked from [RULES.md](../RULES.md)

## Key decisions (from R&D)

| Decision        | Choice                                                |
| --------------- | ----------------------------------------------------- |
| Scheduler       | GitHub Actions (public repo free tier)                |
| Database        | Supabase PostgreSQL (free tier)                       |
| Frontend host   | GitHub Pages (not Vercel — stay in GitHub)            |
| AI              | Hugging Face models on **runner**, not cloud LLM APIs |
| Scanner pattern | Plugin SDK + per-source modules                       |

## Next phase

→ [Phase 2: Foundation + CI/CD](../phase-02-foundation-cicd/)
