# AI Job Hunter — Project Vision

## Mission

Automate job discovery, scoring, resume tailoring, and application tracking at **₹0 operational cost** using GitHub (Pages + Actions), Supabase, and open-source Hugging Face models.

## Product pillars

| Pillar     | Description                                                                     |
| ---------- | ------------------------------------------------------------------------------- |
| **Scan**   | Plugin-based job discovery from Greenhouse, Lever, Ashby, Workday, career pages |
| **Score**  | HF models on GitHub Actions runners — no paid LLM APIs                          |
| **Tailor** | LaTeX resume generation with ATS validation; master resume is read-only         |
| **Track**  | Dashboard on GitHub Pages backed by Supabase                                    |
| **Learn**  | Feedback loop from applied/rejected/interview outcomes                          |

## Constraints

- GitHub-only hosting for control plane
- Supabase free tier for data plane
- No VPS, no paid AI APIs in CI/production
- Production-ready increments only — never skip phases

## Repository map

```text
.ai/           AI operating system (start here)
apps/          dashboard, api
packages/      scanner-sdk, database, config, (ai-engine, resume-engine — future)
scanners/      Per-source plugins
scraper/       Scan pipeline orchestration
supabase/      Schema + migrations
docs/          Human-facing architecture and phase specs
.github/       CI/CD, security, deployment
```

## For AI agents

1. Read `.ai/AGENTS.md` first
2. Check `.ai/EXECUTION_PLAN.md` for current phase
3. Search → Reuse → Refactor → Create (never duplicate)
4. Complete `.ai/REVIEW_CHECKLIST.md` before finishing

Human docs: [`README.md`](../README.md) · Research: [`docs/deep-research-report.md`](../docs/deep-research-report.md)
