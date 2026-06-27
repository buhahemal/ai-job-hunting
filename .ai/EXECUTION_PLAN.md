# Execution Plan

Incremental delivery. **Never skip phases.** Each phase is production-ready before the next begins.

| Phase | Focus                         | Status      | Spec                                |
| ----: | ----------------------------- | ----------- | ----------------------------------- |
|     1 | Research & Architecture       | done        | [phase-01.md](./phases/phase-01.md) |
|     2 | Foundation + CI/CD            | done        | [phase-02.md](./phases/phase-02.md) |
|     3 | Supabase schema + integration | done        | [phase-03.md](./phases/phase-03.md) |
|     4 | Scanner SDK + Greenhouse      | done        | [phase-04.md](./phases/phase-04.md) |
|     5 | Remaining scanners            | done        | [phase-05.md](./phases/phase-05.md) |
|     6 | AI pipeline (Hugging Face)    | in_progress | [phase-06.md](./phases/phase-06.md) |
|     7 | Resume engine (LaTeX → PDF)   | pending     | [phase-07.md](./phases/phase-07.md) |
|     8 | Dashboard backend             | pending     | [phase-08.md](./phases/phase-08.md) |
|     9 | Dashboard frontend            | pending     | [phase-09.md](./phases/phase-09.md) |
|    10 | Learning engine + analytics   | pending     | [phase-10.md](./phases/phase-10.md) |
|    11 | Production hardening          | pending     | [phase-11.md](./phases/phase-11.md) |

## Dependency chain

```text
P1 → P2 → P3 → P4 → P5 → P6 → P7
P3 → P8 → P9 → P10 → P11
```

## Marking a phase complete

1. Check all deliverables in `docs/phases/phase-XX-*/STATUS.md`
2. Run full quality pipeline (`npm run quality`)
3. Update phase table above and `docs/phases/README.md`
4. Set next phase to `in_progress`
