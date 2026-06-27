# AI Job Hunter - Engineering Execution Plan & Project Rules

## Project Rules
This project must be developed incrementally. Every phase must be production-ready before moving to the next phase.
The AI must never skip phases.
The AI must not generate placeholder implementations.

Every feature must include:
* Design
* Implementation
* Unit tests
* Integration tests
* Documentation
* Code review
* Performance review
* Security review

A phase is considered complete only after all quality gates pass.

---

## Development Phases

### Phase 0 — Research & Architecture
Deliverables:
* Technical Design Document
* Architecture Diagram
* Database Schema
* API Design
* Folder Structure
* Technology Decisions
* Risk Analysis
* Cost Analysis (₹0 only)
* Dependency Analysis
No implementation.

---

### Phase 1 — Foundation
Deliverables:
* Repository setup
* Monorepo structure
* TypeScript
* ESLint
* Prettier
* Husky
* Commitlint
* GitHub Actions
* Docker
* Environment management
* Logging
* Configuration system
No business logic.

---

### Phase 2 — Database
Design: Supabase
Tables, Indexes, RLS, Policies, Migrations, Seed Data, ER Diagram, Database Tests.

---

### Phase 3 — Job Scanner Engine
This is the highest priority.
Implement:
* Scanner SDK
* Plugin architecture
* Queue
* Retry
* Rate Limiter
* Deduplication
* Normalization
* Caching
* Scheduler
Supported Sources: Greenhouse, Lever, Ashby, Workday, Company Career Pages, RemoteOK, Wellfound, etc.
Every scanner should expose:
* `discoverJobs()`
* `normalize()`
* `healthCheck()`
Tests required.

---

### Phase 4 — AI Processing
Build:
* Job Parser
* Skill Extractor
* Salary Extractor
* Resume Matcher
* AI Score
* Keyword Extraction
* Semantic Similarity
* Duplicate Detection
* LLM abstraction layer

---

### Phase 5 — Resume Engine
Master Resume -> LaTeX -> Generate -> PDF -> Store -> Version -> ATS Validation.
Never modify the master resume.

---

### Phase 6 — Dashboard Backend
REST APIs, Authentication, Caching, Search, Filtering, Pagination, Analytics.

---

### Phase 7 — Dashboard Frontend
Next.js / React, Dashboard, Jobs, Companies, Resume, Applications, Analytics, Responsive, Accessibility.

---

### Phase 8 — AI Learning Engine
Learn from: Applied, Rejected, Ignored, Interview, Offer. Update scoring automatically.

---

### Phase 9 — Production
Monitoring, Logging, Metrics, Performance, Backup, Documentation, Deployment.

---

## AI Coding Rules
* Behavior: Principal Engineer.
* Never generate code before designing it.
* Before implementing anything explain: Design, Trade-offs, Complexity, Security, Scalability.
* Never create duplicate code.
* Always prefer reusable abstractions.
* Never hardcode values. Use dependency injection.
* Every function must be documented.
* Every public method must have tests.
* Every API must have OpenAPI documentation.

---

## AI Review Rules
Perform these reviews after every completed feature:
* **Architecture Review**: SOLID, Clean Architecture, Modular Design, Separation of Concerns, Dependency Direction.
* **Security Review**: OWASP, Secrets, Injection, SSRF, XSS, CSRF, Authentication, Authorization, Rate Limiting, Input Validation.
* **Performance Review**: N+1, Memory, CPU, Parallelism, Indexes, Caching, Streaming, Pagination.
* **Database Review**: Indexes, Normalization, Foreign Keys, Transactions, Deadlocks, Query Plans.
* **AI Review**: Prompt Quality, Model Selection, Token Usage, Latency, Caching, Hallucination Risk.
* **Code Quality Review**: Cyclomatic Complexity, Naming, Duplication, Maintainability, Readability, Documentation.
* **Test Review**: Coverage, Edge Cases, Failure Cases, Retry Logic, Mocking, Integration.
* **Cost Review**: Verify everything remains within ₹0 budget. Reject paid services. Prefer open-source alternatives.

---

## Definition of Done
A feature is complete only if:
✓ Builds successfully
✓ Tests pass
✓ Lint passes
✓ Type checking passes
✓ Documentation updated
✓ Architecture review passed
✓ Security review passed
✓ Performance review passed
✓ Cost review passed
✓ GitHub Actions pass
Otherwise the feature is incomplete.
