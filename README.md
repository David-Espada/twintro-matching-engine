# Twintro Professional Matching Engine

A working local MVP for the Twintro Hackathon: compare two professionals or rank a network using **THDE-1.0**, a deterministic Hybrid Decision Engine. Local Sentence Transformers supply semantic evidence. An optional language model explains results after scoring; no API key is needed.

## Why Twintro Hybrid Decision Engine?

Traditional similarity systems answer: **“How similar are these professionals?”** Twintro additionally answers: **“Can their strengths create professional value together?”**

**Affinity ≠ Complementarity.** Professional Affinity is the existing six-dimension weighted score. Collaboration Potential is the complementarity component, shown independently with its own classification. A low affinity and high complementarity can both be correct: professionals may work in different areas while bringing useful strengths together. Complementarity still contributes exactly 15% when all affinity dimensions are available; no weights or scores are inflated for presentation.

Every result includes a deterministic **Professional Connection Insight**. “High” means at least 80 for each score, matching the Strong classification boundary. Missing complementarity is unavailable, not zero. The UI preserves both scores and labels, including lower-affinity results.

## Architecture

```text
Next.js dashboard (TypeScript / Tailwind / shadcn/ui / Lucide)
       | JSON HTTP requests / CORS
       v
FastAPI routes -> application services -> profile repository
       |                                  |
       v                                  v
Profile validation & normalization   PostgreSQL + pgvector
       |                             profiles / cached vectors / history
       v                                  |
Structured + semantic + complementarity <- hybrid candidate retrieval
       |
       v
Deterministic weighted score + confidence + evidence
       |
       v
Template explanation OR optional OpenAI explanation
       |
       v
Result / ranked candidates / execution metrics
```

The monorepo contains `frontend/`, `backend/`, `dataset/`, `scripts/`, and `docs/`. Backend services separate normalization, embeddings, six component scorers, ranking, and justification. Pydantic validates API input; SQLAlchemy persists profiles and match history. NumPy and scikit-learn handle vector operations. The embedding interface allows replacement providers.

## Quick start with Docker

Install Docker Desktop with Linux containers. In PowerShell, from this repository:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose logs -f backend
```

Open **http://localhost:3000** for the dashboard and **http://localhost:8000/docs** for Swagger. The first backend startup downloads the local embedding model and seeds 100 profiles. Subsequent starts reuse model files and unchanged stored vectors. The database uses host port **5433** to avoid an existing PostgreSQL instance on 5432; containers use internal port 5432.

```powershell
docker compose ps
docker compose down
```

Named volumes retain the database and model cache. The included Docker credentials are for local development. Services bind to localhost.

## Native development (Windows)

Prerequisites: Python **3.12+** (tested on Python 3.13), Node **22+**, npm, and Docker Desktop for PostgreSQL/pgvector. Use the virtual environment executable directly to avoid PowerShell activation-policy issues.

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e './backend[dev]'
docker compose up -d db
.\.venv\Scripts\python.exe scripts/seed_database.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

In a second terminal:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

On macOS/Linux, use `python3`, `.venv/bin/python`, and `npm` instead. Local backend configuration reads the repository `.env` even if started from `backend/`. For a nondefault frontend API origin, create `frontend/.env.local` containing `NEXT_PUBLIC_API_URL=...` and rebuild/restart Next.js.

The demo-profile endpoint and inline matching work without a database connection; history persistence is best effort in that mode. Stored profile operations and stored-pool ranking require PostgreSQL. The actual embedding model remains required; the app does not silently replace semantic inference with a fake scorer. Internet is required for the first model download, then local cached inference works offline. Windows can use ordinary copied model cache files without developer mode or administrator access.

## Configuration

| Variable | Default / purpose |
| --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://twintro:twintro@localhost:5433/twintro` |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` |
| `EMBEDDING_DIMENSIONS` | `384`; must match model and schema |
| `OPENAI_API_KEY` | Empty; deterministic template explanation |
| `OPENAI_MODEL` | `gpt-4.1-mini`; used only if a key is present |
| `CORS_ORIGINS` | JSON list, default `["http://localhost:3000"]` |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000`; a frontend build-time variable |
| `NEXT_PUBLIC_DEMO_MODE` | `true` in `.env.example`; badge and recommended selector group only; defaults to `false` when unset |
| `FULL_SCAN_THRESHOLD` | `10000` |
| `SEMANTIC_RETRIEVAL_LIMIT` | `200` |
| `COMPLEMENTARITY_RETRIEVAL_LIMIT` | `100` |

Never put an OpenAI key in a `NEXT_PUBLIC_` variable. The optional explanation provider uses [Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) and automatically falls back if its request fails.

For native frontend development, put `NEXT_PUBLIC_DEMO_MODE=true` in `frontend/.env.local`. For Docker, set it in the root `.env` and rebuild the frontend image. Next.js embeds this flag at build time. Demo mode never bypasses the API or changes scores; set it to `false` and rebuild to hide the badge and recommendations.

## Matching formula

```text
Skills             30%  = exact overlap 40% + concept similarity 60%
Role               20%  = semantic 70% + role-family relationship 30%
Industry           15%  = exact / configured relation / semantic fallback
Experience         10%  = experience-band proximity
Interests          10%  = exact overlap 40% + concept similarity 60%
Complementarity    15%  = role relationship 70% + skill-domain relationship 30%

Affinity = sum(available component score * weight) / sum(available weights)
```

Components already use the 0–100 scale. Missing components are `null`, omitted from the weighted mean. API affinity uses one decimal place. Confidence is independent: mean profile completeness × available dimension weight, bounded to 0–1. Fully populated profiles have confidence 1. Identical complete profiles can score above 90 without reaching 100 because complementarity is not the same as similarity; the exact complementarity also depends on their skill-domain relationships.

Classification: Exceptional ≥90, Strong ≥80, Good ≥70, Moderate ≥60, Low ≥40, Weak <40. With no evidence, the UI reports insufficient information instead of displaying a measured compatibility percentage.

See [the full decision contract](docs/architecture.md) for cosine aggregation, symmetric matrices, fractional experience bands, tie ordering, unknown taxonomy handling, model-change procedures, and operational boundaries.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | API/database state and engine version |
| GET | `/api/v1/profiles/demo` | Synthetic demo profiles without database dependency |
| GET | `/api/v1/profiles?limit=100&offset=0` | Paginated stored profiles and total |
| GET | `/api/v1/profiles/{user_id}` | Stored professional |
| POST | `/api/v1/profiles` | Validated profile upsert; cache embeddings |
| POST | `/api/v1/match/1-to-1` | Compare `profile_a` and `profile_b` |
| POST | `/api/v1/match/1-to-n` | Rank inline `candidate_pool` or stored profiles |
| GET | `/docs` | Interactive OpenAPI documentation |
| GET | `/openapi.json` | Machine-readable contract |

### Example request (PowerShell)

```powershell
$profiles = Invoke-RestMethod http://localhost:8000/api/v1/profiles/demo
$body = @{ profile_a = $profiles[3]; profile_b = $profiles[7] } | ConvertTo-Json -Depth 10
Invoke-RestMethod http://localhost:8000/api/v1/match/1-to-1 -Method Post -ContentType 'application/json' -Body $body

$ranking = @{ source_profile = $profiles[3]; candidate_pool = $profiles; limit = 20; justify_top = 5 }
Invoke-RestMethod http://localhost:8000/api/v1/match/1-to-n -Method Post -ContentType 'application/json' -Body ($ranking | ConvertTo-Json -Depth 10)
```

Omit `candidate_pool` (or use null) to query PostgreSQL. An explicit empty array evaluates zero candidates. Duplicate candidate IDs are rejected; the source user is excluded. `limit` is 1–100, default 20; `justify_top` is 0–100, default 5. Inline input is capped at 50,000 profiles. Request time includes retrieval, inference, explanations and the history-write attempt.

Actual captured example responses are in [docs/example-match.json](docs/example-match.json) and [docs/example-ranking.json](docs/example-ranking.json). Responses include original profiles, affinity, classification, confidence, six components, shared/related skills, complementary strengths, explanation/provider, engine version and execution time. Ranking adds evaluated count, pool size, retrieval mode and limit.

Excerpt from the captured default comparison (the complete response is linked above):

```json
{
  "match_mode": "1-to-1",
  "affinity_percentage": 38.7,
  "match_level": "Weak Match",
  "confidence": 1.0
}
```

This pair has strong complementarity but limited similarity in other dimensions. The engine preserves the formula rather than inflating affinity for the demo. Follow the [presentation walkthrough](docs/demo-guide.md) to demonstrate this distinction, identical profiles, missing data, and stored-profile ranking.

## Demo data and database

```powershell
python scripts/generate_profiles.py --count 100
python scripts/generate_profiles.py --count 1000 --output dataset/profiles-1000.json
python scripts/generate_profiles.py --count 10000 --output dataset/profiles-10000.json
.\.venv\Scripts\python.exe scripts/seed_database.py --input dataset/profiles-1000.json
```

Generation is reproducible (`--seed 42`), with role-specific skill sets and plausible experience. The checked-in dataset contains 100 synthetic people, including 12 curated profiles with stable IDs and an intentionally unrelated restaurant operations example. [Nine recommended demo pairs](docs/demo-cases.md) cover near-identical, similar, complementary, moderate, and unrelated relationships. Run `python scripts/audit_demo.py` with the installed backend to regenerate the real-model audit. Seeding is idempotent, processed in batches, and reports newly generated vectors. It upserts supplied IDs and does not delete existing profiles. For a bare database, `python -m app.core.database` enables pgvector and creates tables/indexes; seeding already performs this initialization.

`professional_profiles` stores original and normalized values, role family, skill domains, JSONB skills/interests, experience, summary, model/hash, vector and timestamps. It has HNSW cosine, GIN domain, and role-family indexes. `match_history` stores versioned result snapshots. Future schema changes need explicit migrations; initialization does not alter existing column definitions.

## Verification

Real stored-network scalability is measured through **50,000 profiles**. See the [scalability report](docs/scalability-report.md) for cold/warm timings, recall, actual HNSW plans and exact score-equivalence evidence, and the [50k presentation guide](docs/large-network-demo.md) for the reproducible case. The 100-profile demo dataset and UI remain available independently of the stored network.

Ranking metadata now separates `total_network_size` from the actual retrieved `candidate_pool_size` and `profiles_fully_scored`. The expandable **Engine metrics** panel shows these counts, branch counts, retrieval backend and measured stage timings. `profiles_evaluated` remains an alias for fully scored profiles; clients relying on the old network meaning of `candidate_pool_size` should use `total_network_size`.

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
$env:RUN_INTEGRATION='1'
..\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:RUN_INTEGRATION
cd ..
.\.venv\Scripts\ruff.exe check --config backend/pyproject.toml backend scripts
cd frontend
npm.cmd test
npm.cmd run build
npx.cmd playwright install chromium
npx.cmd playwright test
```

Backend unit tests inject a deterministic test embedding fixture, so they do not need a model download. Opt-in integration tests exercise real MiniLM semantics, real PostgreSQL/pgvector retrieval, persistence and cache invalidation, with database changes rolled back. Browser tests require the running seeded backend and frontend, and cover desktop/mobile matching, ranking, directory filtering, explanation rendering and manually entered incomplete profiles.

```powershell
.\.venv\Scripts\python.exe scripts/benchmark.py --count 100
.\.venv\Scripts\python.exe scripts/benchmark.py --count 10000 --output docs/benchmark-10000.json
```

Benchmark output distinguishes cold/warm engine passes and includes actual evaluated counts. Numbers depend on CPU/model cache and exclude HTTP, persistence and optional external explanations. See [validation notes](docs/validation.md) for the checks run in this workspace.

The [earlier benchmark report](docs/benchmark-report.md) preserves pre-optimization 100/1,000/10,000-profile measurements. Current database-backed results and reproduction instructions are in the [scalability report](docs/scalability-report.md); `scripts/scalability_suite.py` measures all five network sizes and recall using a separate small/empty database without deleting existing data.

Detailed match responses also expose `complementarity_level`, `connection_insight`, `target_role_family`, `target_normalized_industry`, and up to three `evidence_tags`. Every ranked item includes those fields and full comparison evidence; expanding a result makes no extra HTTP request. Entries outside `justify_top` show their deterministic insight instead of requesting another explanation. Minimum affinity, minimum complementarity, role family, and industry filters act only on returned top results and preserve backend ordering and original rank numbers; they do not search the entire pool or recalculate scores.

## Dashboard

- **Overview:** live database status, network count, matching entry points and formula visualization.
- **1-to-1 Match:** demo selectors or manual profiles, six score bars, confidence, evidence and explanation.
- **1-to-N Ranking:** demo or stored pool, selectable limit, metrics and expandable detailed comparisons.
- **Professional Profiles:** searchable/filterable demo and paginated stored profiles, plus profile creation/updating.
- **Engine Explanation:** visual pipeline and full formula for the hackathon presentation.

The interface uses original dark/green styling and locally maintained shadcn/ui Button primitives. No proprietary Twintro assets or fake frontend scores are included.
