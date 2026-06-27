# Profile and Resume Guide

Your **Profile** is the single source of truth for job matching and resume generation.

## What the profile controls

| Section                                                    | Used by                                        |
| ---------------------------------------------------------- | ---------------------------------------------- |
| Personal info, summary, skills, experience, projects       | Scanner matching, embedding text, gap analysis |
| Target roles                                               | Experience match score                         |
| Match preferences (locations, remote, companies, keywords) | Remote/company/location sub-scores             |
| Match settings → minimum score                             | Promotion threshold for Job Leads              |
| Master LaTeX (auto-generated on save)                      | Skill corpus + resume fallback                 |

## Recommended workflow

1. Open **Profile & Settings** in the dashboard.
2. Import structured JSON (`profile.json` or `master.json` format) or fill fields manually.
3. Save profile — the API regenerates master LaTeX from your structured data.
4. Optionally enable **Re-score Scan Insights** when changing match settings.
5. Tailor a job from Job Leads — preview LaTeX and download PDF when compiled.

## API endpoints

- `GET /api/profile` — load profile
- `POST /api/profile` — save profile (`{ profile, rescan?: boolean }`)
- `POST /api/profile/import` — merge JSON import
- `POST /api/jobs/:id/tailor` — tailor + publish PDF
- `GET /api/jobs/:id/resumes` — list resume versions

## Sync behavior

The GitHub `sync-profile` workflow **seeds Supabase only when the profile is empty**. Dashboard edits are preserved after the first seed.

## Backend requirements

- Profile import and LaTeX regeneration require the Python API (`VITE_USE_BACKEND=true`).
- PDF compilation requires `pdflatex` (included in the API Docker image and CI).
