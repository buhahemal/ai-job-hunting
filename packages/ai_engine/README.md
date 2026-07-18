# AI Engine (Phase 6)

Local, zero-API-key job matching for the scanner pipeline.

## Model

**`sentence-transformers/all-MiniLM-L6-v2`** (Python equivalent of Xenova/all-MiniLM-L6-v2)

| Property             | Value                      |
| -------------------- | -------------------------- |
| Parameters           | ~22M                       |
| Embedding dimensions | 384                        |
| Model size           | ~80–90 MB                  |
| Runner RAM           | ~200–500 MB typical on CPU |

Chosen for GitHub Actions `ubuntu-latest` because it is small, fast on CPU, and produces stable semantic embeddings without GPU or paid APIs.

## Scoring method

1. Build candidate text from profile (`skills`, roles, experience, preferences).
2. Build job text from title, company, location, description.
3. Encode both with MiniLM (L2-normalized vectors).
4. Compute cosine similarity and scale to **0–100%** match score.
5. No conversational LLM output is generated during scoring.

## Fallback order

1. **Embedding scorer** (default, ₹0)
2. **Heuristic scorer** — always available offline fallback

Paid LLM APIs (Gemini, OpenAI, etc.) are **not** used in the production pipeline.

## Salary extraction

Deterministic regex/heuristics in `salary_extractor.py` — extracts `$120k`, `35 LPA`, `€80,000`, etc. from job descriptions without LLM hallucination.

## Duplicate detection

1. URL / source+id / title similarity (SequenceMatcher)
2. Embedding cosine similarity ≥ `AI_DUPLICATE_THRESHOLD` (default 0.92) on title+company+description

## Environment variables

| Variable                   | Default                                               | Description                               |
| -------------------------- | ----------------------------------------------------- | ----------------------------------------- |
| `HF_HOME`                  | `~/.cache/huggingface`                                | Hugging Face model cache directory        |
| `AI_EMBEDDING_MODEL`       | `sentence-transformers/all-MiniLM-L6-v2`              | Override embedding model                  |
| `AI_SCORER`                | `embedding`                                           | Force `embedding` or `heuristic`          |
| `AI_DUPLICATE_THRESHOLD`   | `0.92`                                                | Embedding cosine threshold for duplicates |
| Variable                   | Default (see `packages/database/python/constants.py`) | Description                               |
| `SCANNER_MIN_MATCH_SCORE`  | `90`                                                  | Jobs must score above this to persist     |
| `SCANNER_MIN_JOBS_PER_RUN` | `25`                                                  | Target qualifying jobs per scan           |

## Tests

```bash
pip install -r packages/ai_engine/requirements.txt
PYTHONPATH=. python3 -m unittest discover -s packages/ai_engine/tests
```

Unit tests mock the embedding model — no model download required in CI test runs.
