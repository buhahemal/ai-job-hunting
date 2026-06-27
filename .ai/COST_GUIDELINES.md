# Cost Guidelines

**Budget: ₹0.** Reject any change that adds recurring cost.

## Approved (free tier)

| Service         | Tier            | Usage                        |
| --------------- | --------------- | ---------------------------- |
| GitHub          | Free            | Pages, Actions, CodeQL       |
| Supabase        | Free            | Postgres + REST              |
| Hugging Face    | Free OSS models | Inference on GH runner       |
| Public job APIs | Free            | Greenhouse boards, Arbeitnow |

## Prohibited in CI/production

- OpenAI, Gemini, Claude, Anthropic APIs
- Paid VPS / cloud compute beyond free tiers
- Paid monitoring SaaS

## GitHub Actions minutes

- Keep workflows parallel but lean
- Cache npm dependencies
- Scanner cron: daily, not hourly
- Nightly tests: scheduled only

## Review question

Before merge: **Does this change increase operational cost?** If yes → find open-source alternative or reject.
