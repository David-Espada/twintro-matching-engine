# Final-demo polish audit

The existing THDE-1.0 architecture, six affinity weights, taxonomy relations, and numeric component algorithms are retained. New labels, insights, evidence tags, and filter metadata are derived after scoring. No frontend scores or fabricated demo results were introduced.

## Product changes

- Separate Professional Affinity and Collaboration Potential cards expose the two scores, separate classifications, helper text, and shared confidence context.
- Centralized complementarity labels use the existing classification boundaries. Missing complementarity returns null and is shown as unavailable.
- Professional Connection Insight is deterministic for all four high/lower combinations. High means ≥80; missing evidence has a separate message. The full numeric classifications remain visible.
- Ranked items expose both scores, role family, normalized industry, at most three evidence tags, and complete comparison evidence. Expanding even an item outside `justify_top` requires no additional request.
- Four optional filters narrow only the returned ranking and retain original rank numbers. The UI states this limitation and distinguishes a filtered empty view from an empty candidate pool.
- Demo mode adds a badge and recommended selectors without changing scoring. The network contains 100 complete synthetic profiles across 23 roles, including 12 curated entries and nine measured demonstration pairs.
- The engine explanation flow separates representation generation, deterministic scoring, and optional narration, and explicitly states that the language model does not calculate scores.

## Error-handling audit

| Condition | Behavior and verification |
| --- | --- |
| Backend connection unavailable | Actionable connection message; fetch unit test and browser network-abort case |
| Database unavailable | Stored operations return JSON 503 with CORS; inline matching remains usable and history failure rolls back; API tests |
| Embedding model unavailable | Explicit `EmbeddingUnavailableError` and actionable JSON 503 with CORS; provider and API tests, browser error-display case |
| Invalid profile input | Pydantic 422 for blank names/invalid experience; frontend renders validation messages |
| Empty candidate pool | Empty results and zero evaluated count; does not need embedding inference |
| Duplicate candidate IDs | Explicit 422 validation error; source ID excluded from eligible candidates |
| Duplicate concepts / unknown taxonomy | Deduplication preserves scoring; unfamiliar concepts receive semantic handling without invented shared domains |
| OpenAI unavailable or blank output | Deterministic template fallback; computed score objects are isolated from provider mutation |
| Non-JSON service errors / timeout | Understandable frontend messages rather than parser errors |

## Changed and added files

The repository was initially uncommitted, so Git lists the project as untracked; this inventory identifies the files changed for this polish task specifically.

- Backend contracts and presentation: `backend/app/schemas/matching.py`, `backend/app/services/matching/scoring.py`, `matching_engine.py`, new `connection_insight.py`, `backend/app/services/justification/template_provider.py`, `justification_service.py`.
- Error handling and empty-pool optimization: `backend/app/main.py`, `backend/app/services/embeddings/sentence_transformer_provider.py`, new `errors.py`, `backend/app/services/ranking/ranking_engine.py`.
- Backend tests: new `backend/tests/test_connection_insight.py`, new `test_embedding_errors.py`; expanded `test_api.py`, `test_integration.py`, `test_matching_1_to_n.py`, `test_justification.py`.
- Frontend contracts/helpers: `frontend/lib/types.ts`, `api.ts`, new `demo.ts`, new `ranking.ts`; expanded `api.test.ts`, new `demo.test.ts`, new `ranking.test.ts`.
- Frontend presentation: `frontend/components/match-result.tsx`, `profile-card.tsx`, `shell.tsx`; new `score-summary.tsx`, `ranking-results.tsx`, `ranking-filters.tsx`, `engine-flow.tsx`; `frontend/app/page.tsx`, `ranking/page.tsx`, `engine/page.tsx`, `globals.css`.
- Browser checks: `frontend/e2e/workflows.spec.ts`.
- Dataset and reproducible tooling: `dataset/professional_profiles.json`, `scripts/generate_profiles.py`, new `demo_profiles.py`, new `audit_demo.py`, new `benchmark_suite.py`.
- Demo configuration: `.env.example`, `.gitignore`, `docker-compose.yml`, `frontend/Dockerfile`. Local ignored `.env` and `frontend/.env.local` enable demo mode in this workspace.
- Documentation/artifacts: `README.md`, `docs/architecture.md`, `demo-guide.md`, `validation.md`, `example-match.json`, `example-ranking.json`; new `demo-cases.md`, `demo-audit.json`, `benchmark-report.md`, `benchmark-100.json`, `benchmark-1000.json`; refreshed `benchmark-10000.json` and this audit.

## Evidence and limits

See [validation results](validation.md), [measured benchmarks](benchmark-report.md), and [recommended demo cases](demo-cases.md). Raw benchmark and demo-audit JSON files contain measured observations, not score fixtures used by the app.

The 10,000-profile full scan remains a noticeable wait. Benchmarks are one sequential cold/warm pair per dataset size on a shared workstation, not latency percentiles, a concurrency test, or an HNSW recall study. MiniLM is less effective on some specialized product names. Post-ranking filters cannot recover candidates outside the requested top results. The optional OpenAI failure path is verified; no successful paid OpenAI call was made. This remains a local hackathon deployment, with the public-hosting limitations documented in `architecture.md`.
