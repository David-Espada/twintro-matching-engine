"""Idempotently import profiles and cache their embeddings in PostgreSQL."""

import argparse
import json
from pathlib import Path
from time import perf_counter

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.core.database import get_engine, initialize_database
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfessionalProfile
from sqlalchemy.orm import Session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "dataset/professional_profiles.json",
    )
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    start_time = perf_counter()
    profiles = [
        ProfessionalProfile.model_validate(p) for p in json.loads(args.input.read_text(encoding="utf-8"))
    ]
    initialize_database()
    with Session(get_engine()) as session:
        repository = ProfileRepository(session)
        totals = dict(profiles_created=0, profiles_updated=0, embeddings_generated=0)
        for start in range(0, len(profiles), 500):
            repository.upsert_many(profiles[start : start + 500], get_matcher().embeddings, get_settings())
            for key in totals:
                totals[key] += repository.last_seed_stats[key]
            print(f"Seeded {min(start + 500, len(profiles))}/{len(profiles)}", flush=True)
    totals["seeding_time_seconds"] = round(perf_counter() - start_time, 3)
    print(json.dumps(totals, indent=2))
    if args.report:
        args.report.write_text(json.dumps(totals, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
