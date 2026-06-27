# Phase 4 — Scanner SDK + Job Sources

**Status:** complete

## Deliverables

- [x] `packages/scanner_sdk` — BaseScanner, registry, HTTP, normalize, config
- [x] Scanner plugins (no subscription, public APIs):
  - Greenhouse (`GREENHOUSE_BOARD_TOKENS`)
  - Lever (`LEVER_COMPANY_SITES`)
  - SmartRecruiters (`SMARTRECRUITERS_COMPANIES`)
  - Teamtailor (`TEAMTAILOR_COMPANY_SLUGS`)
  - Workable (`WORKABLE_ACCOUNT_SLUGS`)
  - RemoteOK (no config)
  - We Work Remotely RSS (no config)
  - Company career pages (Google, Microsoft, EPAM, Globant, Datadog, Stripe)
- [x] Unit tests for normalize + registry
- [x] `.env.example` and `scanners/README.md`

## Spec

[`docs/phases/phase-04-scanner-sdk-greenhouse/`](../docs/phases/phase-04-scanner-sdk-greenhouse/)
