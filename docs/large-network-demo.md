# 50,000-profile presentation

Open http://localhost:3000/ranking, select **Taylor Okafor — AI Engineer** (`usr_00004`, Healthcare, six years), choose **Stored PostgreSQL profiles**, request **5** results, and click **Find Best Matches**. Expand **Engine metrics**. Run one warmup request before presenting.

Measured stored-network run: **50,000 network profiles → 200 semantic + 100 complementary → 300 unique candidates → 300 full THDE evaluations**. Warm service time: **127.76 ms**; application-cold: **3832.82 ms**. Current UI timings will vary by machine/runtime and include explanations when requested.

| Rank | Profile ID | Professional | Role | Affinity | Complementarity |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | usr_05372 | Noah Vega | AI Engineer | 93.2% | 55.0% |
| 2 | usr_07176 | Kai Singh | AI Engineer | 93.2% | 55.0% |
| 3 | usr_19672 | Noah Park | AI Engineer | 93.2% | 55.0% |
| 4 | usr_32586 | Avery Park | AI Engineer | 93.2% | 55.0% |
| 5 | usr_34654 | Leo Kim | AI Engineer | 93.2% | 55.0% |

> Twintro searched a network of 50,000 professionals, reduced it to approximately a few hundred high-potential candidates, and then applied the full explainable Decision Engine.

This statement is supported by the measured 300-candidate run. Do not claim all 50,000 received THDE scoring or that approximate retrieval guarantees the global best five. All five observed affinities tie; the deterministic user-ID tiebreak orders them. Index rebuilds can change membership at retrieval cutoffs.

Expand any result to show its complete six-part breakdown. Explain that retrieval selects candidates; the unchanged THDE formula decides their scores. The language model does not calculate the score.

The regular demo remains available via **Demo profiles** (100 profiles, full scan). The checked-in demo JSON and curated profile IDs are preserved even when PostgreSQL contains 50k.

To recreate the large dataset in an existing smaller database:

```powershell
.\.venv\Scripts\python.exe scripts/generate_profiles.py --count 50000 --seed 42 --output dataset/profiles-50000.json
.\.venv\Scripts\python.exe scripts/seed_database.py --input dataset/profiles-50000.json --report docs/my-seeding.json
.\.venv\Scripts\python.exe scripts/benchmark_stored.py --output docs/my-50000.json
```

Seeding upserts without deleting other IDs; the displayed network is exactly 50,000 only if no additional profiles have been added. See [measured results and methodology](scalability-report.md), [raw top-five artifact](scalability-50000.json), and [recall evidence](retrieval-quality.json).
