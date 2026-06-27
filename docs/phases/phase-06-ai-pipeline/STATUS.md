# Phase 6 — AI Processing Pipeline (Hugging Face on GitHub Runner)

```yaml
status: in_progress
started: 2026-06-27
completed:
```

## Deliverables

- [x] `packages/ai_engine/` — modular AI layer with embedding-first scoring
- [x] **Scoring:** `sentence-transformers/all-MiniLM-L6-v2` cosine similarity → 0–100%
- [x] **Skill extraction:** keyword overlap from job description (no LLM)
- [ ] **Salary extraction:** regex/heuristics (no hallucination)
- [ ] **Duplicate detection:** embedding similarity threshold
- [ ] Remove/replace `google-genai` from resume tailoring (Phase 7)
- [x] GitHub Actions runs inference on `ubuntu-latest` runner
- [x] Model cache via Actions cache (`HF_HOME`)
- [x] Scanner match gate: score > 90%, target 3 jobs per run
- [x] Fallback chain: embeddings → optional Gemini (secret) → heuristic

## Models (from R&D)

| Task         | Model                                                      |
| ------------ | ---------------------------------------------------------- |
| Similarity   | `sentence-transformers/all-MiniLM-L6-v2`                   |
| Resume JSON  | `nakamoto-yama/t5-resume-generation` (Phase 7 uses output) |
| Summarize JD | `facebook/bart-large-cnn` (optional)                       |

## Workflow

`scanner-cron.yml`: cache HF model → scan → dedupe → **embedding score** → write Supabase.

## Rules

- Default path is ₹0 local embeddings on GitHub runner
- Gemini only when `GEMINI_API_KEY` secret is explicitly configured
- Never invent experience or fabricate projects in AI output
- Log model name and job count — not prompts with PII

## Quality gate

- [x] Unit tests with mocked model outputs
- [ ] Scoring validated in Actions under 15 min job budget (manual workflow_dispatch)
- [x] Cost review: ₹0 default path confirmed

## Next phase

→ [Phase 7: Resume Engine](../phase-07-resume-engine/)
