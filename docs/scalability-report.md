# Measured 1-to-N scalability

Measured 2026-10-04 on Windows 11, Python 3.13.14, Intel64 Family 6 Model 183 Stepping 1, GenuineIntel. PostgreSQL runs in Docker Desktop; the benchmark client/model run on Windows CPU. Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions). THDE-1.0 and all six weights are unchanged.

## Audit and method

The [pre-change audit](retrieval-audit.md) records the original switch and queries. All five measurements below use the actual stored PostgreSQL network through MatchService, with source usr_00004, limit 5 and justify_top=0. Each size gets a fresh Python process: cold includes model imports/loading and empty concept caches; warm immediately reuses them. Model files were already downloaded and HF_HUB_OFFLINE=1 avoids download checks. PostgreSQL/OS caches were not flushed, so this is **application-cold, not disk-cold**. Times include database reads, retrieval, THDE, sorting and match-history persistence; exclude Python process startup, generation, seeding, HTTP transfer and optional explanations. One cold/warm observation per size is not a percentile, throughput result, or latency guarantee.

The suite grows the same database from 100 to 50,000 rows and analyzes the table after each stage. It never deletes existing profiles. [Raw stage artifacts](scalability-50000.json) retain counters, top five and stage times.

## Actual database benchmarks

| Network | Mode | Cold ms | Warm ms | Retrieved cold / warm | Fully scored cold / warm |
| ---: | --- | ---: | ---: | ---: | ---: |
| 100 | full | 4,214.45 | 31.97 | 99 / 99 | 99 / 99 |
| 1,000 | full | 3,974.19 | 444.54 | 999 / 999 | 999 / 999 |
| 10,000 | full | 6,781.47 | 2,853.67 | 9,999 / 9,999 | 9,999 / 9,999 |
| 25,000 | hybrid | 3,872.84 | 154.06 | 300 / 300 | 300 / 300 |
| 50,000 | hybrid | 3,832.82 | 127.76 | 300 / 300 | 300 / 300 |

Full mode retrieves all eligible profiles; source exclusion gives N−1. Hybrid uses pgvector top 200 plus up to 100 complementary profiles, deduplicates, and fully scores the union.

| Network | Pass | Vector stage ms | Complementarity stage ms | THDE stage ms | Total ms |
| ---: | --- | ---: | ---: | ---: | ---: |
| 25,000 | cold | 3,691.37 | 64.29 | 96.37 | 3,872.84 |
| 25,000 | warm | 10.53 | 55.62 | 70.74 | 154.06 |
| 50,000 | cold | 3,675.45 | 51.56 | 75.59 | 3,832.82 |
| 50,000 | warm | 7.71 | 45.41 | 53.43 | 127.76 |

Vector stage includes encoding the source, transaction-local HNSW settings, SQL execution and result materialization. Its cold model load dominates. Complementarity stage includes SQL relationship ranking and union conversion. THDE stage includes batched concept preparation, every comparison, sorting and setting result modes. The remaining total includes network counts, orchestration and history persistence. The 50k warm observation being faster than 25k is run variability, not evidence of decreasing complexity.

## Profile-driven optimization and score equivalence

The unchanged 10k warm engine pass measured **19,658.95 ms** in this session; after optimization it measured **2,150.47 ms** (9.14×). These engine-only measurements are separate from the database table above and the previous phase’s ~12s observation. No model inference was required for new concepts after warmup.

The [before cProfile](profile-before.txt) captured 48,870 concept cosine calls, 39.09s cumulative in concept_similarity and 23.86s in 195,480 generic check_array calls (nested times overlap). Normalization consumed 3.75s, including 2.54s resolving role families. Instrumentation raises runtime: these are bottleneck attribution figures, not user latency.

Changes: dense NumPy L2 normalization and matrix multiplication reproduce the original sklearn cosine; the same skill matrix supplies score and evidence; bounded caches reuse canonical terms, role-family and skill-domain resolution. Existing batched concept embeddings remain. Full database reads defer unused embedding columns. Seed batches use one bulk upsert rather than one statement per profile, with current-model, hash, dimension, finite-value and nonzero checks before vector reuse.

The [after cProfile](profile-after.txt) has 38,871 cosine calls, 1.77s cumulative there, and 0.22s normalization. All **9,999** captured component scores, affinities, confidence values and rank positions are exactly equal before/after at API precision. Raw arrays are additionally tested against sklearn for float32/float64, zero and near-zero vectors within 1e-7 absolute / 1e-6 relative tolerance. No weights, thresholds for match labels, or scoring formula terms changed.

## Actual pgvector verification

The [catalog and EXPLAIN ANALYZE artifact](pgvector-verification.json) confirms pgvector 0.8.7, column `vector(384)`, 50,000 vectors of dimension 384, and the expected model ID. The cosine HNSW index is `ix_profiles_embedding_hnsw`, declared without storage overrides (pgvector defaults m=16, ef_construction=64). Both recorded plans actually contain an Index Scan using that index.

- audited_defaults: ef_search=40, iterative_scan=off; requested 200, returned **120**, SQL execution **0.888 ms**.
- production: ef_search=400, iterative_scan=strict_order; requested 200, returned **200**, SQL execution **2.128 ms**.

The audited default settings underfilled the request on this network. The production query now uses transaction-local ef_search=400 and strict iterative scanning. Iterative scanning requires pgvector ≥0.8; its configured scan limits can still constrain recall on other filters/networks. These settings and default index parameters follow the [official pgvector documentation](https://github.com/pgvector/pgvector#iterative-index-scans). No planner settings force index usage in the recorded plans.

## Retrieval quality

Evaluation used **the same complete 10,000-row PostgreSQL network** for full THDE ground truth and forced hybrid retrieval, before growing it further. Six source profiles cover AI/data, product, marketing, sales, design and security. Recall@K is the fraction of the full THDE top K IDs present in the retrieved union, with the engine’s normal deterministic tie ordering. It is not embedding-neighbor recall or an estimate of all-50k THDE recall. [Raw per-source IDs and results](retrieval-quality.json) permit checking each fraction.

| Source role | Recall@5 | Recall@10 | Recall@20 | Retrieved |
| --- | ---: | ---: | ---: | ---: |
| AI Engineer | 100.0% | 100.0% | 100.0% | 300 |
| Product Manager | 100.0% | 100.0% | 100.0% | 299 |
| Marketing Manager | 60.0% | 80.0% | 90.0% | 300 |
| Sales Manager | 100.0% | 100.0% | 100.0% | 300 |
| UX Designer | 60.0% | 50.0% | 60.0% | 300 |
| Cybersecurity Engineer | 100.0% | 100.0% | 95.0% | 300 |
| **Average** | **86.7%** | **88.3%** | **90.8%** | — |

Quality is imperfect: UX and marketing lose high-THDE candidates. Whole-profile semantic similarity does not equal the six-factor THDE objective; the complementarity branch prioritizes structural relations and breaks ties by ID. HNSW adds approximation and equal-distance cutoff variation. The scorer is unchanged for retrieved candidates, but hybrid cannot promise the global THDE top K.

## Threshold recommendation

Retain **FULL_SCAN_THRESHOLD=10000**, configurable in settings/environment. The measured 10k stored full ranking is now 2.85s warm, while 25k/50k hybrid is ~0.13–0.15s warm. Keeping full scans through 10k preserves exact rankings on manageable networks given the recall losses above. For a strict subsecond interactive requirement, the measured 1k full result (0.44s) supports an explicitly configured threshold of 1000, with the documented recall tradeoff. A production SLO needs concurrent, repeated measurements and relevance acceptance criteria. The switch remains strictly greater than eligible count threshold: a stored source at network size 10,001 still leaves 10,000 eligible candidates and uses full mode.

## Reproducible seeding

Seed 42, 50,000 unique profile IDs, profession-specific archetypes and the same 12 curated profiles (IDs 81–92). The checked-in 100-profile demo file is preserved; the generated large JSON is ignored by Git/Docker and reproducible. Names and professional archetypes intentionally repeat; these are synthetic profiles, not 50,000 distinct observed careers.

| Resulting network | Created in stage | Updated in stage | Profile vectors generated | Seeding seconds |
| ---: | ---: | ---: | ---: | ---: |
| 100 | 0 | 0 | 0 | 0.112 |
| 1,000 | 900 | 0 | 900 | 7.661 |
| 10,000 | 9,000 | 0 | 9,000 | 30.276 |
| 25,000 | 15,000 | 0 | 15,000 | 39.031 |
| 50,000 | 25,000 | 0 | 25,000 | 53.370 |

Totals: 49,900 created (100 already existed), 0 changed profile records, 49,900 newly persisted profile vectors, 130.450s seeding, excluding benchmark/evaluation pauses. Vector count is per profile requiring a vector; identical representation texts can reuse the provider cache. Updated counts mean changed profile content, not SQL rows touched by an idempotent upsert.

A [complete unchanged 50k reseed](scalability-reseed.json) created 0, updated 0, generated **0** vectors in 56.598s.

## API, UI and failure behavior

`total_network_size` includes a stored source; `candidate_pool_size` now means the actual deduplicated retrieved set (previously it meant eligible network size). `profiles_fully_scored` is the number passed through the full engine, and `profiles_evaluated` remains its compatibility alias. `semantic_candidates` and `complementarity_candidates` count each branch before union; full mode reports zero for these branches. `retrieval_backend` is pgvector, numpy (large inline pools), or none (full). The compact, initially collapsed Engine metrics panel displays actual response values.

A vector SQL failure returns the existing understandable HTTP 503; there is no successful hybrid result or silent fallback. Tests inject a failure specifically after network counting to verify this.

## Reproduction

Install the existing backend dependencies and download/warm the model first. With the current 50k database, rerun `scripts/benchmark_stored.py --output docs/my-50000.json` and `scripts/verify_pgvector.py`. To reproduce all five sizes and manageable-pool recall without deleting existing data, use a separate database:

```powershell
docker compose exec -T db createdb -U twintro twintro_scalability
$env:DATABASE_URL='postgresql+psycopg://twintro:twintro@localhost:5433/twintro_scalability'
$env:HF_HUB_OFFLINE='1'
.\.venv\Scripts\python.exe scripts/scalability_suite.py
.\.venv\Scripts\python.exe scripts/verify_pgvector.py
.\.venv\Scripts\python.exe scripts/seed_database.py --input dataset/profiles-50000.json --report docs/scalability-reseed.json
Remove-Item Env:DATABASE_URL
```

On an empty reproduction database, the first stage reports 100 creations rather than zero. The suite calls evaluate_retrieval at 10k before growing further. For a standalone recall run, point DATABASE_URL at a manageable seeded database and run `scripts/evaluate_retrieval.py`; the default guard refuses more than 10k rows rather than quietly evaluating a different pool. The generator supports `--count 50000 --seed 42 --output dataset/profiles-50000.json`.

## Remaining limits

- Six synthetic source cases and one pass per scale do not establish production recall or p95 latency.
- Warm speed depends on a resident model; application-cold requests still take several seconds.
- Complementarity SQL and exact counts still inspect the network; THDE is bounded, total work is not constant time.
- HNSW is approximate; rebuilds and equal-vector cutoffs can change candidate membership. Final ordering is stable for a fixed set.
- Large inline pools must encode all supplied profiles and do not gain indexed PostgreSQL retrieval.
- No concurrent-load, million-profile, mixed-model migration or production-capacity claim is made.

See [the reproducible 50k presentation](large-network-demo.md) and [validation / changed-file inventory](scalability-validation.md).
