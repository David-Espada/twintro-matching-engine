"""Capture a warm 10k full-scan profile and reference scores before/after optimization."""

import argparse
import cProfile
import json
import pstats
from pathlib import Path
from time import perf_counter

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.schemas.profile import ProfessionalProfile
from app.services.ranking.ranking_engine import RankingEngine
from generate_profiles import generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="before")
    args = parser.parse_args()
    profiles = [ProfessionalProfile.model_validate(p) for p in generate(10000)]
    engine = RankingEngine(get_matcher(), get_settings())
    engine.matcher.prepare(profiles)
    start = perf_counter()
    result = engine.rank(profiles[3], profiles, limit=10000)
    elapsed = (perf_counter() - start) * 1000
    output = Path("docs") / f"profile-{args.label}"
    output.with_suffix(".json").write_text(
        json.dumps(
            {
                "warm_time_ms": elapsed,
                "scores": [
                    {
                        "id": r.target_user.user_id,
                        "affinity": r.affinity_percentage,
                        "breakdown": r.score_breakdown.model_dump(),
                        "confidence": r.confidence,
                    }
                    for r in result.results
                ],
            }
        ),
        encoding="utf-8",
    )
    profiler = cProfile.Profile()
    profiler.runcall(engine.rank, profiles[3], profiles, 20)
    with output.with_suffix(".txt").open("w", encoding="utf-8") as stream:
        pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("cumulative").print_stats(45)
    print(f"{args.label}: {elapsed:.2f} ms", flush=True)


if __name__ == "__main__":
    main()
