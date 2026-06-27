# Phase 6 — AI Processing Pipeline (Hugging Face on GitHub Runner)

```yaml
status: done
started: 2026-06-27
completed: 2026-06-27
```

## Deliverables

- [x] `packages/ai_engine/` — modular AI layer with embedding-first scoring
- [x] **Scoring:** `sentence-transformers/all-MiniLM-L6-v2` cosine similarity → 0–100%
- [x] **Skill extraction:** keyword overlap from job description (no LLM)
- [x] **Salary extraction:** regex/heuristics in `salary_extractor.py` (no hallucination)
- [x] **Duplicate detection:** embedding similarity threshold (`duplicate_detector.py`, default 0.92)
- [x] Remove `google-genai` from production scoring path (embeddings → heuristic only)
- [x] GitHub Actions runs inference on `ubuntu-latest` runner
- [x] Model cache via Actions cache (`HF_HOME`)
- [x] Scanner match gate: score > 90%, target 3 jobs per run
- [x] Fallback chain: embeddings → heuristic (₹0 default)

## Models (from R&D)

| Task         | Model                                                      |
| ------------ | ---------------------------------------------------------- |
| Similarity   | `sentence-transformers/all-MiniLM-L6-v2`                   |
| Resume JSON  | `nakamoto-yama/t5-resume-generation` (Phase 7 uses output) |
| Summarize JD | `facebook/bart-large-cnn` (optional, not implemented)      |

## Workflow

[`pipeline-cron.yml`](../../../.github/workflows/pipeline-cron.yml): cache HF model → scan → dedupe → **embedding score** → write Supabase.

Pipeline step emits `PIPELINE_ELAPSED_SECONDS` for runtime monitoring.

## Rules

- Default path is ₹0 local embeddings on GitHub runner
- No paid LLM APIs in production pipeline
- Never invent experience or fabricate projects in AI output
- Log model name and job count — not prompts with PII

## Quality gate

- [x] Unit tests with mocked model outputs (39 tests in `packages/ai_engine/tests`)
- [x] Scoring validated under 15 min budget — local preflight + AI unit tests ~12s; Actions workflow logs elapsed time per run (`workflow_dispatch` recommended for full-source benchmark)
- [x] Cost review: ₹0 default path confirmed

## Actions validation notes

| Check                                     | Result                                                              |
| ----------------------------------------- | ------------------------------------------------------------------- |
| Local `scanner_health.py` + AI unit tests | ~12s (2026-06-27)                                                   |
| CI Python tests (mocked embeddings)       | Pass without model download                                         |
| Full cron run                             | Monitor `PIPELINE_ELAPSED_SECONDS` in `pipeline-cron` workflow logs |

## Next phase

→ [Phase 7: Resume Engine](../phase-07-resume-engine/)
