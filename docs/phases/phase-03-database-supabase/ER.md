# Phase 3 — Entity Relationship Diagram

```mermaid
erDiagram
  profiles ||--o{ jobs : "scores against"
  jobs ||--o{ interviews : has
  jobs ||--o{ applications : tracks
  jobs ||--o{ resumes : "tailored PDFs"
  companies ||--o{ jobs : "sources via scanners"

  profiles {
    text id PK
    jsonb data
    timestamptz updated_at
  }

  jobs {
    text id PK
    text source
    text external_id UK
    text title
    text company
    text location
    text remote_type
    text url
    text description
    timestamptz posted_at
    text status
    int score
    jsonb extracted_skills
  }

  interviews {
    text id PK
    text job_id FK
    text role
    text company
    timestamptz interview_date
    text status
  }

  applications {
    uuid id PK
    text job_id FK
    timestamptz applied_at
    text result
  }

  companies {
    text name PK
    text career_url
    timestamptz last_scan
  }

  resumes {
    uuid id PK
    text job_id FK
    text version
    jsonb content
    text pdf_url
  }
```

## Notes

- **profiles**: single row (`id = default`) stores full profile JSON for scoring and resume tailoring.
- **jobs**: unique on `(source, external_id)`; pipeline upserts via service role from GitHub Actions.
- **RLS**: anon key (GitHub Pages) can read/update; pipeline writes use service role.
