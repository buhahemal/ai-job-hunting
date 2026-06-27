# Cost Guidelines

**Budget: ₹0.** Reject any change that adds recurring cost.

## Approved (free tier)

| Service         | Tier            | Usage                       |
| --------------- | --------------- | --------------------------- |
| GitHub          | Free            | Pages, Actions, CodeQL      |
| Supabase        | Free            | Postgres + REST             |
| Hugging Face    | Free OSS models | Inference on GH runner      |
| Public job APIs | Free            | Greenhouse boards, RemoteOK |

## Prohibited in CI/production (default path)

- OpenAI, Claude, Anthropic APIs
- Paid VPS / cloud compute beyond free tiers
- Paid monitoring SaaS

## Optional opt-in (not default)

- **Gemini** — allowed only when `GEMINI_API_KEY` is explicitly configured as a fallback after local embedding scoring fails, or for resume tailoring during development

## GitHub Actions minutes

- Keep workflows parallel but lean
- Cache npm dependencies
- Cache Hugging Face models (`~/.cache/huggingface`) in scanner cron
- Scanner cron: daily, not hourly
- Nightly tests: scheduled only

## Review question

Before merge: **Does this change increase operational cost?** If yes → find open-source alternative or reject.
