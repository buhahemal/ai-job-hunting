# MNC Scanner Tuning Design

## Goal

Increase useful job leads for global-remote and India searches while keeping the
GitHub Actions scanner within the free-tier runtime budget.

## Configuration

- Use a 75% promotion threshold in Python, TypeScript, environment examples,
  GitHub Actions, and the current Supabase profile.
- Keep profile `matchSettings.minMatchScore` as the authoritative per-user
  threshold. The workflow environment value is the fallback.
- Limit scheduled runs to four discovery passes, 200 jobs per source, and 500
  newly evaluated jobs.
- Continue using the free Hugging Face embedding model.

## MNC Greenhouse Seeds

Check in a curated list of public Greenhouse boards that were verified against
the Greenhouse Job Board API on 2026-07-19:

- India/global-remote priority: Twilio, GitLab, Okta, Elastic, New Relic,
  Datadog, Coinbase, MongoDB, Rubrik, Sumo Logic, and Cloudflare.
- Additional global-remote coverage: Stripe, Cockroach Labs, Samsara, Airbnb,
  Dropbox, Reddit, Pinterest, Affirm, and Grafana Labs.

Remove the invalid `hashicorp` board token. User-supplied environment values
continue to merge with these defaults without replacing them.

## Data Flow

1. `ATS_DISCOVERY_ENABLED=true` loads the reviewed board seeds.
2. Explicit GitHub secrets are merged with the seed list.
3. Greenhouse divides each pass limit across configured boards.
4. Jobs are normalized, preference-filtered, scored, and persisted as scan
   insights.
5. Jobs scoring at least the profile threshold are promoted to Job Leads.

## Reliability and Testing

- Seed tests verify that values are non-empty and unique.
- Existing merge behavior remains covered.
- Run focused scanner tests, spellcheck, the full quality pipeline, and tests.
- No API keys or credentials are committed.

## Acceptance Criteria

- The default Greenhouse seed list contains exactly the 20 validated boards.
- No invalid `hashicorp` token remains.
- Default and current-user promotion thresholds are 75%.
- Pipeline Cron uses four passes, a 200 per-source cap, and 500 evaluations.
- Scanner configuration tests and repository quality gates pass.
