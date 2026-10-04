# Workspace validation

Validated on October 4, 2026 (America/La_Paz), using Windows, Python 3.13, Node 24, and PostgreSQL 17 with pgvector in Docker.

## Completed checks

- 82 pytest cases pass with `RUN_INTEGRATION=1`: all original checks plus separate complementarity classification, four deterministic insights, unknown/duplicate concepts, unavailable database/model, blank/failed explanation fallback, API summary fields, empty-pool inference avoidance, and nine real-model demo relationships. The suite contains 71 unit/API cases and 11 opt-in integration cases.
- 11 Vitest cases pass: backend-only scores, stored versus inline pool requests, explicit empty pools, four post-ranking filters, preserved ordering, missing complementarity, demo-mode grouping, validation/connection errors, non-JSON failures and timeouts.
- 14 Playwright scenarios pass across desktop Chromium and mobile Chromium: all existing flows plus both score cards, connection insight, ranking filters, three-tag limit, original ranking order, no additional matching HTTP requests on expansion, demo badge/recommendations and backend/database/model error displays. The final suite completed in 7.6 seconds. The main navigation flows recorded no browser JavaScript errors.
- Next.js production build and TypeScript checks pass for all five pages.
- Ruff checks pass. Python dependency resolution passes `pip check`.
- npm audit reports no known frontend dependency vulnerabilities at verification time.
- PostgreSQL seeding imports 100 profiles; an unchanged second import generates **0** embeddings.
- Actual API responses are captured in `example-match.json` and `example-ranking.json`.
- Both updated Docker images build successfully. `docker compose up -d --wait` starts the complete stack; the backend and database health checks pass. All 14 browser workflows pass against the containerized app with `NEXT_PUBLIC_DEMO_MODE=true`.
- The final database check confirms 100 professional profiles and persisted match-history records. The application is left running at localhost ports 3000 (frontend), 8000 (API) and 5433 (PostgreSQL).

## Measured full-ranking performance

The native CPU suite uses 100, 1,000 and 10,000 synthetic profiles. It excludes the source and ranks all eligible candidates with the real local model, with no test embeddings or fake scores.

| Profiles | Cold engine (ms) | Warm engine (ms) | Evaluated | Retrieval |
| ---: | ---: | ---: | ---: | --- |
| 100 | 4,959.61 | 130.31 | 99 | full |
| 1,000 | 6,199.39 | 1,357.92 | 999 | full |
| 10,000 | 16,708.90 | 12,002.02 | 9,999 | full |

See [benchmark methodology and raw outputs](benchmark-report.md). These timings exclude HTTP, database history writes and optional external explanations; they are observations on this machine, not latency guarantees. Model files were already cached on disk for all runs.

## Limits of verification

The optional OpenAI path was tested with a failing injected provider to confirm fallback and score isolation. No paid OpenAI request was made. Unit tests and local model/database integration are separate so routine testing does not require network downloads. A Starlette/AnyIO deprecation warning is emitted by the native test client and does not affect test results.

Hybrid SQL vector and complementarity retrieval was exercised against the seeded database, including deduplication, source exclusion and unknown-role inputs. The 10,000-profile benchmark covers full scanning; it is not an HNSW recall study or a load/concurrency test. MiniLM's relationship between FastAPI and backend development is weaker than its relationship between PostgreSQL and SQL; the implementation does not manufacture stronger evidence.

The app is a locally deployable hackathon MVP. Public multi-user hosting still needs the controls listed in `architecture.md`.

The [final-demo audit](final-demo-audit.md) contains the changed-file inventory, feature summary and error-handling matrix. The original default pair still measures 38.7% affinity and 95% complementarity; the UI now explains and displays both independently.
