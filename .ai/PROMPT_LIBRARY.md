# Prompt Library

Reusable prompts for AI coding agents working in this repo.

## PR review

```text
Review this Pull Request.

Find: duplicate code, duplicate business logic, unused functions, dead code,
existing utilities that should be reused, architecture violations, circular
dependencies, large functions, memory issues, performance bottlenecks,
security issues, missing tests, missing documentation.

Suggest a better implementation aligned with .ai/CODING_RULES.md.
```

## New scanner

```text
Implement a scanner for [SOURCE] in scanners/[name]/ following
packages/scanner-sdk/python/base.py. Register in registry.py.
Add unit tests. Use packages/scanner-sdk/python/http.py and normalize.py.
No duplicate HTTP or normalization logic.
```

## Generate tests

```text
Add meaningful unit tests for [MODULE]. Follow .ai/TESTING.md.
Mock external HTTP. Use existing test patterns in the repo.
Do not add trivial assertions.
```

## Optimize SQL

```text
Review supabase/migrations/ for query patterns in [FEATURE].
Suggest indexes, FK constraints, and RLS policies.
Ensure idempotent migrations.
```

## Architecture review

```text
Review [CHANGE] against .ai/ARCHITECTURE.md and .ai/REVIEW_CHECKLIST.md.
Verify package boundaries, dependency direction, and ₹0 cost.
```

## Resume tailoring (Phase 7)

```text
Tailor resume wording for job [ID] using master resume as read-only source.
Never invent experience, employers, or projects. Optimize keywords only.
```

## Definition of done

```text
Verify against .ai/REVIEW_CHECKLIST.md and .ai/AGENTS.md Definition of Done.
Run: npm run quality && npm test
```
