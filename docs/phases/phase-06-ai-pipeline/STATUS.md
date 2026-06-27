# Phase 6 — AI Processing Pipeline (Hugging Face on GitHub Runner)

```yaml
status: pending
started:
completed:
```

## Deliverables

- [ ] `packages/ai-engine/` — modular AI layer (no Gemini/OpenAI in production)
- [ ] **Scoring:** `sentence-transformers/all-MiniLM-L6-v2` + heuristic features (skills, seniority, remote, company prefs)
- [ ] **Skill extraction:** keyword + embedding overlap from job description
- [ ] **Salary extraction:** regex/heuristics (no hallucination)
- [ ] **Duplicate detection:** embedding similarity threshold
- [ ] Remove/replace `google-genai` / Gemini from scraper pipeline
- [ ] GitHub Actions job runs inference on `ubuntu-latest` runner
- [ ] Model cache via Actions cache (`HF_HOME`)
- [ ] Batch only top-N new jobs per run (respect 2000 min/month budget)
- [ ] Fallback to heuristic-only if model load fails

## Models (from R&D)

| Task | Model |
|------|-------|
| Similarity | `all-MiniLM-L6-v2` |
| Resume JSON | `nakamoto-yama/t5-resume-generation` (Phase 7 uses output) |
| Summarize JD | `facebook/bart-large-cnn` (optional) |

## Workflow

Merge `scanner-cron.yml` steps: scan → dedupe → **HF score** → write Supabase.

## Rules

- **Never** call paid LLM APIs in CI or production
- **Never** invent experience or fabricate projects in AI output
- Log model name, duration, job count — not prompts with PII

## Quality gate

- [ ] Scoring runs in Actions under 15 min job budget
- [ ] Unit tests with mocked model outputs
- [ ] Cost review: ₹0 confirmed

## Next phase

→ [Phase 7: Resume Engine](../phase-07-resume-engine/)
