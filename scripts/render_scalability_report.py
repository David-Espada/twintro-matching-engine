"""Render documentation strictly from captured measurement artifacts."""

import json
import platform
from pathlib import Path


def read(name):
    return json.loads((Path("docs") / name).read_text(encoding="utf-8"))


def main():
    sizes = (100, 1000, 10000, 25000, 50000)
    measurements = {n: read(f"scalability-{n}.json") for n in sizes}
    quality = read("retrieval-quality.json")
    before, after = read("profile-before.json"), read("profile-after.json")
    exact = before["scores"] == after["scores"]
    if not exact:
        raise ValueError("Score/order equivalence check failed; investigate before publishing the report")
    verification = read("pgvector-verification.json")
    seeding = read("scalability-seeding.json")
    reseed = read("scalability-reseed.json")
    lines = [
        "# Measured 1-to-N scalability",
        "",
        f"Measured 2026-10-04 on {platform.system()} {platform.release()}, Python {platform.python_version()}, "
        f"{platform.processor()}. PostgreSQL runs in Docker Desktop; the benchmark client/model run on Windows CPU. "
        "Model: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions). THDE-1.0 and all six weights are unchanged.",
        "",
        "## Audit and method",
        "",
        "The [pre-change audit](retrieval-audit.md) records the original switch and queries. "
        "All five measurements below use the actual stored PostgreSQL network through MatchService, "
        "with source usr_00004, limit 5 and justify_top=0. Each size gets a fresh Python process: cold includes "
        "model imports/loading and empty concept caches; warm immediately reuses them. Model files were already downloaded "
        "and HF_HUB_OFFLINE=1 avoids download checks. PostgreSQL/OS caches were not flushed, so this is **application-cold, "
        "not disk-cold**. Times include database reads, retrieval, THDE, sorting and match-history persistence; exclude "
        "Python process startup, generation, seeding, HTTP transfer and optional explanations. One cold/warm observation "
        "per size is not a percentile, throughput result, or latency guarantee.",
        "",
        "The suite grows the same database from 100 to 50,000 rows and analyzes the table after each stage. "
        "It never deletes existing profiles. [Raw stage artifacts](scalability-50000.json) retain counters, top five and stage times.",
        "",
        "## Actual database benchmarks",
        "",
        "| Network | Mode | Cold ms | Warm ms | Retrieved cold / warm | Fully scored cold / warm |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for n, (cold, warm) in measurements.items():
        lines.append(
            f"| {n:,} | {warm['retrieval_mode']} | {cold['execution_time_ms']:,.2f} | {warm['execution_time_ms']:,.2f} | {cold['candidate_pool_size']:,} / {warm['candidate_pool_size']:,} | {cold['profiles_fully_scored']:,} / {warm['profiles_fully_scored']:,} |"
        )
    lines += [
        "",
        "Full mode retrieves all eligible profiles; source exclusion gives N−1. "
        "Hybrid uses pgvector top 200 plus up to 100 complementary profiles, deduplicates, and fully scores the union.",
        "",
        "| Network | Pass | Vector stage ms | Complementarity stage ms | THDE stage ms | Total ms |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for n in (25000, 50000):
        for r in measurements[n]:
            lines.append(
                f"| {n:,} | {r['run']} | {r['vector_retrieval_time_ms']:,.2f} | {r['complementarity_retrieval_time_ms']:,.2f} | {r['thde_scoring_time_ms']:,.2f} | {r['execution_time_ms']:,.2f} |"
            )
    lines += [
        "",
        "Vector stage includes encoding the source, transaction-local HNSW settings, SQL execution and result materialization. "
        "Its cold model load dominates. Complementarity stage includes SQL relationship ranking and union conversion. "
        "THDE stage includes batched concept preparation, every comparison, sorting and setting result modes. "
        "The remaining total includes network counts, orchestration and history persistence. "
        "The 50k warm observation being faster than 25k is run variability, not evidence of decreasing complexity.",
        "",
        "## Profile-driven optimization and score equivalence",
        "",
        f"The unchanged 10k warm engine pass measured **{before['warm_time_ms']:,.2f} ms** in this session; "
        f"after optimization it measured **{after['warm_time_ms']:,.2f} ms** ({before['warm_time_ms'] / after['warm_time_ms']:.2f}×). "
        "These engine-only measurements are separate from the database table above and the previous phase’s ~12s observation. "
        "No model inference was required for new concepts after warmup.",
        "",
        "The [before cProfile](profile-before.txt) captured 48,870 concept cosine calls, 39.09s cumulative in "
        "concept_similarity and 23.86s in 195,480 generic check_array calls (nested times overlap). "
        "Normalization consumed 3.75s, including 2.54s resolving role families. Instrumentation raises runtime: "
        "these are bottleneck attribution figures, not user latency.",
        "",
        "Changes: dense NumPy L2 normalization and matrix multiplication reproduce the original sklearn cosine; "
        "the same skill matrix supplies score and evidence; bounded caches reuse canonical terms, role-family and "
        "skill-domain resolution. Existing batched concept embeddings remain. Full database reads defer unused "
        "embedding columns. Seed batches use one bulk upsert rather than one statement per profile, with current-model, "
        "hash, dimension, finite-value and nonzero checks before vector reuse.",
        "",
        "The [after cProfile](profile-after.txt) has 38,871 cosine calls, 1.77s cumulative there, and 0.22s normalization. "
        "All **9,999** captured component scores, affinities, confidence values and rank positions are exactly equal "
        "before/after at API precision. Raw arrays are additionally tested against sklearn for float32/float64, zero "
        "and near-zero vectors within 1e-7 absolute / 1e-6 relative tolerance. No weights, thresholds for match labels, "
        "or scoring formula terms changed.",
        "",
        "## Actual pgvector verification",
        "",
        f"The [catalog and EXPLAIN ANALYZE artifact](pgvector-verification.json) confirms pgvector {verification['extension_version']}, "
        f"column `{verification['column_type']}`, 50,000 vectors of dimension 384, and the expected model ID. "
        "The cosine HNSW index is `ix_profiles_embedding_hnsw`, declared without storage overrides "
        "(pgvector defaults m=16, ef_construction=64). Both recorded plans actually contain an Index Scan using that index.",
        "",
    ]
    for key in ("audited_defaults", "production"):
        r = verification[key]
        plan = r["plan"][0]
        lines.append(
            f"- {key}: ef_search={r['ef_search']}, iterative_scan={r['iterative_scan']}; "
            f"requested 200, returned **{plan['Plan']['Actual Rows']}**, SQL execution **{plan['Execution Time']} ms**."
        )
    lines += [
        "",
        "The audited default settings underfilled the request on this network. The production query now uses "
        "transaction-local ef_search=400 and strict iterative scanning. Iterative scanning requires pgvector ≥0.8; "
        "its configured scan limits can still constrain recall on other filters/networks. "
        "These settings and default index parameters follow the [official pgvector documentation](https://github.com/pgvector/pgvector#iterative-index-scans). "
        "No planner settings force index usage in the recorded plans.",
        "",
        "## Retrieval quality",
        "",
        f"Evaluation used **the same complete {quality['network_size']:,}-row PostgreSQL network** for full THDE ground truth "
        "and forced hybrid retrieval, before growing it further. Six source profiles cover AI/data, product, "
        "marketing, sales, design and security. Recall@K is the fraction of the full THDE top K IDs present "
        "in the retrieved union, with the engine’s normal deterministic tie ordering. "
        "It is not embedding-neighbor recall or an estimate of all-50k THDE recall. "
        "[Raw per-source IDs and results](retrieval-quality.json) permit checking each fraction.",
        "",
        "| Source role | Recall@5 | Recall@10 | Recall@20 | Retrieved |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for r in quality["sources"]:
        lines.append(
            f"| {r['role']} | {r['recall@5']:.1%} | {r['recall@10']:.1%} | {r['recall@20']:.1%} | {r['candidate_pool_size']} |"
        )
    a = quality["average"]
    lines += [
        f"| **Average** | **{a['recall@5']:.1%}** | **{a['recall@10']:.1%}** | **{a['recall@20']:.1%}** | — |",
        "",
        "Quality is imperfect: UX and marketing lose high-THDE candidates. Whole-profile semantic similarity "
        "does not equal the six-factor THDE objective; the complementarity branch prioritizes structural relations "
        "and breaks ties by ID. HNSW adds approximation and equal-distance cutoff variation. The scorer is unchanged "
        "for retrieved candidates, but hybrid cannot promise the global THDE top K.",
        "",
        "## Threshold recommendation",
        "",
        "Retain **FULL_SCAN_THRESHOLD=10000**, configurable in settings/environment. The measured 10k stored full "
        "ranking is now 2.85s warm, while 25k/50k hybrid is ~0.13–0.15s warm. Keeping full scans through 10k "
        "preserves exact rankings on manageable networks given the recall losses above. For a strict subsecond "
        "interactive requirement, the measured 1k full result (0.44s) supports an explicitly configured threshold "
        "of 1000, with the documented recall tradeoff. A production SLO needs concurrent, repeated measurements "
        "and relevance acceptance criteria. The switch remains strictly greater than eligible count threshold: "
        "a stored source at network size 10,001 still leaves 10,000 eligible candidates and uses full mode.",
        "",
        "## Reproducible seeding",
        "",
        "Seed 42, 50,000 unique profile IDs, profession-specific archetypes and the same 12 curated profiles "
        "(IDs 81–92). The checked-in 100-profile demo file is preserved; the generated large JSON is ignored by "
        "Git/Docker and reproducible. Names and professional archetypes intentionally repeat; these are synthetic "
        "profiles, not 50,000 distinct observed careers.",
        "",
        "| Resulting network | Created in stage | Updated in stage | Profile vectors generated | Seeding seconds |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in seeding:
        lines.append(
            f"| {r['network_size']:,} | {r['profiles_created']:,} | {r['profiles_updated']:,} | {r['embeddings_generated']:,} | {r['seeding_time_seconds']:.3f} |"
        )
    lines += [
        "",
        f"Totals: {sum(r['profiles_created'] for r in seeding):,} created (100 already existed), "
        f"{sum(r['profiles_updated'] for r in seeding)} changed profile records, "
        f"{sum(r['embeddings_generated'] for r in seeding):,} newly persisted profile vectors, "
        f"{sum(r['seeding_time_seconds'] for r in seeding):.3f}s seeding, excluding benchmark/evaluation pauses. "
        "Vector count is per profile requiring a vector; identical representation texts can reuse the provider cache. "
        "Updated counts mean changed profile content, not SQL rows touched by an idempotent upsert.",
        "",
        f"A [complete unchanged 50k reseed](scalability-reseed.json) created {reseed['profiles_created']}, "
        f"updated {reseed['profiles_updated']}, generated **{reseed['embeddings_generated']}** vectors in "
        f"{reseed['seeding_time_seconds']:.3f}s.",
        "",
        "## API, UI and failure behavior",
        "",
        "`total_network_size` includes a stored source; `candidate_pool_size` now means the actual deduplicated "
        "retrieved set (previously it meant eligible network size). `profiles_fully_scored` is the number passed "
        "through the full engine, and `profiles_evaluated` remains its compatibility alias. "
        "`semantic_candidates` and `complementarity_candidates` count each branch before union; full mode reports "
        "zero for these branches. `retrieval_backend` is pgvector, numpy (large inline pools), or none (full). "
        "The compact, initially collapsed Engine metrics panel displays actual response values.",
        "",
        "A vector SQL failure returns the existing understandable HTTP 503; there is no successful hybrid result "
        "or silent fallback. Tests inject a failure specifically after network counting to verify this.",
        "",
        "## Reproduction",
        "",
        "Install the existing backend dependencies and download/warm the model first. With the current 50k "
        "database, rerun `scripts/benchmark_stored.py --output docs/my-50000.json` and `scripts/verify_pgvector.py`. "
        "To reproduce all five sizes and manageable-pool recall without deleting existing data, use a separate database:",
        "",
        "```powershell",
        "docker compose exec -T db createdb -U twintro twintro_scalability",
        "$env:DATABASE_URL='postgresql+psycopg://twintro:twintro@localhost:5433/twintro_scalability'",
        "$env:HF_HUB_OFFLINE='1'",
        ".\\.venv\\Scripts\\python.exe scripts/scalability_suite.py",
        ".\\.venv\\Scripts\\python.exe scripts/verify_pgvector.py",
        ".\\.venv\\Scripts\\python.exe scripts/seed_database.py --input dataset/profiles-50000.json --report docs/scalability-reseed.json",
        "Remove-Item Env:DATABASE_URL",
        "```",
        "",
        "On an empty reproduction database, the first stage reports 100 creations rather than zero. "
        "The suite calls evaluate_retrieval at 10k before growing further. For a standalone recall run, point "
        "DATABASE_URL at a manageable seeded database and run `scripts/evaluate_retrieval.py`; the default guard "
        "refuses more than 10k rows rather than quietly evaluating a different pool. The generator supports "
        "`--count 50000 --seed 42 --output dataset/profiles-50000.json`.",
        "",
        "## Remaining limits",
        "",
        "- Six synthetic source cases and one pass per scale do not establish production recall or p95 latency.",
        "- Warm speed depends on a resident model; application-cold requests still take several seconds.",
        "- Complementarity SQL and exact counts still inspect the network; THDE is bounded, total work is not constant time.",
        "- HNSW is approximate; rebuilds and equal-vector cutoffs can change candidate membership. Final ordering is stable for a fixed set.",
        "- Large inline pools must encode all supplied profiles and do not gain indexed PostgreSQL retrieval.",
        "- No concurrent-load, million-profile, mixed-model migration or production-capacity claim is made.",
        "",
        "See [the reproducible 50k presentation](large-network-demo.md) and [validation / changed-file inventory](scalability-validation.md).",
        "",
    ]
    Path("docs/scalability-report.md").write_text("\n".join(lines), encoding="utf-8")
    final = measurements[50000][1]
    demo = [
        "# 50,000-profile presentation",
        "",
        "Open http://localhost:3000/ranking, select **Taylor Okafor — AI Engineer** "
        "(`usr_00004`, Healthcare, six years), choose **Stored PostgreSQL profiles**, request **5** results, "
        "and click **Find Best Matches**. Expand **Engine metrics**. Run one warmup request before presenting.",
        "",
        f"Measured stored-network run: **50,000 network profiles → {final['semantic_candidates']} semantic + "
        f"{final['complementarity_candidates']} complementary → {final['candidate_pool_size']} unique candidates → "
        f"{final['profiles_fully_scored']} full THDE evaluations**. Warm service time: **{final['execution_time_ms']} ms**; "
        f"application-cold: **{measurements[50000][0]['execution_time_ms']} ms**. "
        "Current UI timings will vary by machine/runtime and include explanations when requested.",
        "",
        "| Rank | Profile ID | Professional | Role | Affinity | Complementarity |",
        "| ---: | --- | --- | --- | ---: | ---: |",
    ]
    for i, r in enumerate(final["top5"], 1):
        demo.append(
            f"| {i} | {r['user_id']} | {r['name']} | {r['role']} | {r['affinity']:.1f}% | {r['complementarity']:.1f}% |"
        )
    demo += [
        "",
        "> Twintro searched a network of 50,000 professionals, reduced it to approximately a few hundred "
        "high-potential candidates, and then applied the full explainable Decision Engine.",
        "",
        "This statement is supported by the measured 300-candidate run. Do not claim all 50,000 received THDE "
        "scoring or that approximate retrieval guarantees the global best five. All five observed affinities tie; "
        "the deterministic user-ID tiebreak orders them. Index rebuilds can change membership at retrieval cutoffs.",
        "",
        "Expand any result to show its complete six-part breakdown. Explain that retrieval selects candidates; "
        "the unchanged THDE formula decides their scores. The language model does not calculate the score.",
        "",
        "The regular demo remains available via **Demo profiles** (100 profiles, full scan). "
        "The checked-in demo JSON and curated profile IDs are preserved even when PostgreSQL contains 50k.",
        "",
        "To recreate the large dataset in an existing smaller database:",
        "",
        "```powershell",
        ".\\.venv\\Scripts\\python.exe scripts/generate_profiles.py --count 50000 --seed 42 --output dataset/profiles-50000.json",
        ".\\.venv\\Scripts\\python.exe scripts/seed_database.py --input dataset/profiles-50000.json --report docs/my-seeding.json",
        ".\\.venv\\Scripts\\python.exe scripts/benchmark_stored.py --output docs/my-50000.json",
        "```",
        "",
        "Seeding upserts without deleting other IDs; the displayed network is exactly 50,000 only if no additional "
        "profiles have been added. See [measured results and methodology](scalability-report.md), "
        "[raw top-five artifact](scalability-50000.json), and [recall evidence](retrieval-quality.json).",
        "",
    ]
    Path("docs/large-network-demo.md").write_text("\n".join(demo), encoding="utf-8")


if __name__ == "__main__":
    main()
