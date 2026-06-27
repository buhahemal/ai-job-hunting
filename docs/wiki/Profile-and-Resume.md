# Profile and Resume

How the unified profile drives **job matching** and **resume tailoring**.

## Single source of truth

Runtime data lives in Supabase `profiles.data` (id=`default`). Repo files (`profile.json`, `master.json`) seed an **empty** profile only.

## Profile sections

| Section                         | Used for                                          |
| ------------------------------- | ------------------------------------------------- |
| Personal info + summary         | Resume LaTeX, embedding text                      |
| Skills + target roles           | Skill match, experience match                     |
| Experience, education, projects | Matching corpus + resume content                  |
| Match preferences               | Remote, company, location sub-scores              |
| Match settings (min score)      | Scanner promotion threshold                       |
| Master LaTeX                    | Auto-regenerated on save (advanced edit optional) |

## Workflow

1. **Profile tab** — fill fields or import JSON
2. **Save** — API validates, regenerates LaTeX, optional rescan
3. **Scan Insights** — jobs scored against profile
4. **Job Leads** — promoted jobs above threshold
5. **Tailor** — deterministic reorder for target job → PDF

## API

| Endpoint                    | Purpose                       |
| --------------------------- | ----------------------------- |
| `GET /api/profile`          | Load profile                  |
| `POST /api/profile`         | Save (`{ profile, rescan? }`) |
| `POST /api/profile/import`  | Merge JSON import             |
| `POST /api/jobs/:id/tailor` | Tailor + compile + upload PDF |

Full guide: [docs/guides/profile-and-resume.md](https://github.com/buhahemal/ai-job-hunting/blob/main/docs/guides/profile-and-resume.md)
