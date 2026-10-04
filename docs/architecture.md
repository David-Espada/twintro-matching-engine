# THDE-1.0 decision contract

The backend owns all matching calculations. The web client sends profiles and renders results; it does not calculate affinity. Every component is bounded to 0–100 before aggregation.

| Dimension | Weight | Calculation |
| --- | ---: | --- |
| Skills | 30% | 40% canonical Jaccard overlap + 60% symmetric best-concept cosine |
| Role | 20% | 70% semantic cosine + 30% configured role-family relation |
| Industry | 15% | Exact canonical equality = 100, otherwise configured relation, otherwise cosine |
| Experience | 10% | Difference between experience bands → 100 / 80 / 60 / 40 / 25 |
| Interests | 10% | Same concept algorithm as skills |
| Complementarity | 15% | 70% role complement + 30% skill-domain complement |

For concept lists A and B, compute each individual embedding, normalize it, and construct cosine matrix M. Clamp negative similarities to zero. Semantic similarity is `(mean(max(M, axis=1)) + mean(max(M, axis=0))) / 2`. This treats both directions equally, without embedding the entire skill list as one concept. Exact overlap is intersection size / union size. Lists are deduplicated and sorted internally, preserving display values separately.

`affinity = sum(score * weight for available components) / sum(available weights)`

No additional scaling is applied because component scores are already 0–100. Null components are omitted, never coerced to zero. Complementarity follows the same availability rule internally. When no dimensions are available, the numerical affinity is 0, confidence is 0, and the UI and template explicitly report insufficient evidence. API classification remains the centralized numerical mapping.

Confidence is `mean(profile_a_completeness, profile_b_completeness) * available_weight`. Completeness is the fraction of five fields present: role, industry, nonempty skills, experience (zero counts), nonempty interests. Confidence is a coverage indicator, not a calibrated probability of success. Missing professional summary does not reduce confidence.

## Taxonomy decisions

All mappings live in `backend/app/services/normalization/taxonomy.py`. Pair relations are expanded symmetrically at definition time. Unknown role families use the `other` bucket; two unknown, different titles are not assumed to share a family. Unknown skills do not create a shared `other` domain. Same known role/domain receives a modest complementarity baseline of 40; unrelated pairs receive 10. Explicit useful relationships score 85–95. Identical complete profiles therefore typically score 91 rather than 100, because similarity and complementarity measure different things.

Experience bands are continuous intervals `[0,3)`, `[3,6)`, `[6,10)`, `[10,15)`, and `[15,∞)`, so fractional years have no gaps. Scores do not become zero solely because experience differs.

## Retrieval and persistence

At most 10,000 eligible candidates: full matching with batch preparation and cached unique concept embeddings. More than 10,000 stored candidates: pgvector cosine retrieval (200) plus SQL ranking of explicit role-family and skill-domain complement relationships (100), union by user ID, then full scoring. The source ID is excluded before counting. Inline pools are never silently inserted into the database; oversized inline pools use batched NumPy cosine retrieval in memory with the same complementarity union. They still incur embedding costs for the full input, unlike indexed stored retrieval.

PostgreSQL stores 384-dimensional profile vectors, a model ID, and a hash of the model ID plus canonical profile representation. Upserts regenerate vectors when that hash/model changes or the stored vector fails validity checks. Changing a name or summary alone does not change the representation. Changing the embedding provider/model requires reseeding all profiles; changing vector dimensions requires an explicit schema migration/reindex before reseeding. Never mix model spaces in semantic retrieval. Model artifacts are cached locally; no inference network call is needed after download.

HNSW provides approximate semantic retrieval. Equal-distance retrieval at the cutoff can vary with index contents. The full ranking is deterministic for a fixed candidate set, taxonomy, embedding artifact, and numerical environment. Ranking sorts the API-rounded affinity descending, then confidence descending, then user ID ascending. Execution time is observational and not deterministic.

## Scalability metrics

The scalability phase verified actual HNSW index use at 50,000 rows and added transaction-local `hnsw.ef_search=400` plus `hnsw.iterative_scan=strict_order` (pgvector ≥0.8). See [measured plans and quality](scalability-report.md). Hash-matching vectors are also checked for current model, dimension, finite values and nonzero norm before reuse. Seed batches use bulk upserts; full profile reads omit unused vector deserialization.

Ranking metadata distinguishes network size from the deduplicated retrieved pool and full THDE evaluation count. Branch counts and stage times are measured, and `retrieval_backend` distinguishes `pgvector`, `numpy`, and `none`. `candidate_pool_size` now means the actual retrieved union; `profiles_evaluated` remains the fully-scored compatibility field. Every union member goes through `MatchingEngine.compare`. Dense NumPy cosine calculations and reused skill matrices preserve the same mathematics; taxonomy caches have bounded sizes. Database retrieval failures propagate as explicit 503 responses.

## Explanations

MatchingEngine returns a completed result before JustificationService runs. The optional provider receives a deep copy; its return type is a string. It cannot mutate returned scores. No API key means a deterministic template. Exceptions and empty API responses fall back to that template. OpenAI prompts are explicitly grounded in profile evidence and treat profile text as untrusted. Generative explanations still require review for factual reliability; the deterministic template is the default for reproducible demos. Only the requested top ranking entries receive optional provider explanations. All entries include deterministic connection insights and full evidence; expansion uses that data without an additional HTTP request.

Complementarity classification uses the same 90/80/70/60/40 boundaries as affinity, with a separate label and a null result when unavailable. Deterministic insights use 80 as the high-score boundary on each axis and cover the four combinations; below-threshold includes moderate/good as well as low scores, so the actual numeric labels remain visible. Missing evidence receives an explicit insufficient-data insight. These outputs are derived after scoring and never feed back into the affinity formula. Ranked items expose normalized target role family/industry and evidence tags, so the frontend never reimplements taxonomy or scoring. Filters preserve the backend order and apply only to returned results.

## Operational boundaries

This is a local hackathon MVP with persistent profiles, validation, error handling, and real semantic inference. Authentication, authorization, distributed rate limits, migrations for future schema changes, retention controls, deployment TLS, and a relevance calibration study are not part of the MVP. Keep the included service bindings on localhost; add those controls before shared public deployment. Scores describe professional profile compatibility, not hiring suitability or guaranteed collaboration outcomes.

Profile summary is retained for display/explanation, but does not independently alter the specified six-factor formula. No random affinity, invented work history, hidden bonuses, or LLM scoring is used. The default MiniLM model handles some niche product names weakly (for example FastAPI); the configurable provider and taxonomy permit future evaluation and improvement without changing the formula.

Implementation references: [SentenceTransformer encoding](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html), [pgvector SQLAlchemy support](https://github.com/pgvector/pgvector-python), [Next.js App Router](https://nextjs.org/docs/app/getting-started/installation), [OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create).
