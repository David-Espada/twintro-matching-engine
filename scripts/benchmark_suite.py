"""Run each dataset size in a fresh process and publish only measured results."""

import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    rows = []
    for count in (100, 1000, 10000):
        output = root / "docs" / f"benchmark-{count}.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(root / "scripts/benchmark.py"),
                "--count",
                str(count),
                "--output",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print(completed.stdout, flush=True)
        measurements = json.loads(output.read_text(encoding="utf-8"))
        cold, warm = measurements
        rows.append(
            f"| {count:,} | {cold['execution_time_ms']:,.2f} | {warm['execution_time_ms']:,.2f} | "
            f"{cold['profiles_evaluated']:,} | {cold['candidate_pool_size']:,} | {cold['retrieval_mode']} |"
        )
    report = [
        "# Real-model benchmark validation",
        "",
        f"Measured {datetime.now(ZoneInfo('America/La_Paz')).strftime('%Y-%m-%d %H:%M %Z')} on "
        f"{platform.system()} {platform.release()}, Python {platform.python_version()}. "
        f"CPU: {platform.processor() or 'not reported by the host'}.",
        "",
        "Model: `sentence-transformers/all-MiniLM-L6-v2`, CPU inference, THDE-1.0, unchanged weights. "
        "These are actual measurements from `scripts/benchmark_suite.py`; raw results are in the "
        "corresponding `benchmark-100.json`, `benchmark-1000.json`, and `benchmark-10000.json` files.",
        "",
        "| Generated profiles | Cold engine (ms) | Warm engine (ms) | Profiles evaluated | Candidate pool size | Retrieval mode |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
        *rows,
        "",
        "## Method and limits",
        "",
        "Each size runs in its own Python process, sequentially. The first pass starts with an unloaded "
        "model and an empty in-memory concept cache, but downloaded model files are already on disk. "
        "The second pass reuses that process's model and concept cache. Model imports/loading and matching "
        "are included in cold engine time; Python startup, dataset generation, network downloads, HTTP, "
        "database writes and optional OpenAI explanations are excluded.",
        "",
        "The source is one of the generated profiles and is excluded, so N inputs yield N−1 eligible "
        "candidates. Both passes evaluate the same candidate pool. The generator includes the documented "
        "curated demo profiles, and all scores come from real semantic inference.",
        "",
        "All three sizes use full evaluation under the 10,000-eligible-candidate threshold. "
        "These runs do not measure the >10,000 hybrid branch, HNSW recall, concurrent throughput or "
        "external-service latency. A single cold/warm pair per size is an observation, not a percentile "
        "or performance guarantee. The 10,000-profile pass remains a noticeable wait during a live demo; "
        "use the 100-profile pool for interactive presentation.",
        "",
    ]
    (root / "docs/benchmark-report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()
