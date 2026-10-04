# Real-model benchmark validation

Measured 2026-10-04 02:41 -04 on Windows 11, Python 3.13.14. CPU: Intel64 Family 6 Model 183 Stepping 1, GenuineIntel.

Model: `sentence-transformers/all-MiniLM-L6-v2`, CPU inference, THDE-1.0, unchanged weights. These are actual measurements from `scripts/benchmark_suite.py`; raw results are in the corresponding `benchmark-100.json`, `benchmark-1000.json`, and `benchmark-10000.json` files.

| Generated profiles | Cold engine (ms) | Warm engine (ms) | Profiles evaluated | Candidate pool size | Retrieval mode |
| ---: | ---: | ---: | ---: | ---: | --- |
| 100 | 4,959.61 | 130.31 | 99 | 99 | full |
| 1,000 | 6,199.39 | 1,357.92 | 999 | 999 | full |
| 10,000 | 16,708.90 | 12,002.02 | 9,999 | 9,999 | full |

## Method and limits

Each size runs in its own Python process, sequentially. The first pass starts with an unloaded model and an empty in-memory concept cache, but downloaded model files are already on disk. The second pass reuses that process's model and concept cache. Model imports/loading and matching are included in cold engine time; Python startup, dataset generation, network downloads, HTTP, database writes and optional OpenAI explanations are excluded.

The source is one of the generated profiles and is excluded, so N inputs yield N−1 eligible candidates. Both passes evaluate the same candidate pool. The generator includes the documented curated demo profiles, and all scores come from real semantic inference.

All three sizes use full evaluation under the 10,000-eligible-candidate threshold. These runs do not measure the >10,000 hybrid branch, HNSW recall, concurrent throughput or external-service latency. A single cold/warm pair per size is an observation, not a percentile or performance guarantee. The 10,000-profile pass remains a noticeable wait during a live demo; use the 100-profile pool for interactive presentation.
