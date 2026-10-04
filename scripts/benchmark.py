"""Measure cold and warm full ranking passes with the actual local embedding model."""

import argparse
import json
from pathlib import Path

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.schemas.profile import ProfessionalProfile
from app.services.ranking.ranking_engine import RankingEngine
from generate_profiles import generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, choices=[100, 1000, 10000], default=100)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    profiles = [ProfessionalProfile.model_validate(p) for p in generate(args.count)]
    ranking = RankingEngine(get_matcher(), get_settings())
    reports = []
    for run in ("cold", "warm"):
        result = ranking.rank(profiles[3], profiles)
        reports.append(
            {
                "run": run,
                **result.metadata.model_dump(),
                "top_affinity": result.results[0].affinity_percentage,
            }
        )
    rendered = json.dumps(reports, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
