# Retrieval audit before scalability changes

Audited 2026-10-04, before modifying the ranking implementation.

`MatchService.rank` counts stored rows excluding the source ID. At **strictly more than FULL_SCAN_THRESHOLD (10,000)** it calls `ProfileRepository.hybrid_candidates`; otherwise it loads all eligible rows and passes them to `RankingEngine`. A stored source in a network of 10,001 still leaves 10,000 eligible profiles and uses full scanning.

The repository orders by pgvector cosine distance, filters the source and other embedding models, and requests 200 rows. It separately selects at most 100 rows using role-family and skill-domain complementarity relationships. Their union is deduplicated by user ID. `RankingEngine` calls the same `MatchingEngine.compare` for every selected candidate and sorts by rounded affinity, confidence, then user ID.

Inline pools above the threshold use NumPy semantic retrieval and THDE complementarity selection, **not PostgreSQL**. Previously both paths reported `hybrid` without distinguishing their backend.

The model declares a 384-dimensional vector column and an HNSW `vector_cosine_ops` index, with default index parameters. The query does not configure `hnsw.ef_search` or iterative scanning. Index declaration alone does not prove index use or delivery of all 200 requested rows. Actual catalog and execution-plan evidence is recorded separately in the scalability report.

Existing `candidate_pool_size` means the eligible network, while `profiles_evaluated` means the deduplicated scoring set. Neither branch counts nor stage timings are exposed. Database exceptions propagate to the API's explicit 503 handler; there is no silent retrieval fallback.

Observed optimization candidates to measure: every comparison normalizes both profiles; skills cosine is computed twice (score and evidence); each cosine call invokes scikit-learn validation and normalization; repository full scans deserialize unused vectors; seeding issues one upsert per row. No formula changes are authorized.
