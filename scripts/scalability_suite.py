"""Grow a seeded DB through five sizes, measuring stored ranking at each size.

Requires an existing network no larger than 100 profiles; never deletes user data.
Use a separate empty PostgreSQL database to reproduce after the 50k run.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from time import perf_counter

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.core.database import get_engine, initialize_database
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfessionalProfile
from generate_profiles import generate
from sqlalchemy import text
from sqlalchemy.orm import Session


def main():
    os.environ["HF_HUB_OFFLINE"] = "1"
    initialize_database()
    profiles = [ProfessionalProfile.model_validate(p) for p in generate(50000, seed=42)]
    Path("dataset/profiles-50000.json").write_text(
        json.dumps([p.model_dump() for p in profiles]), encoding="utf-8"
    )
    reports = []
    with Session(get_engine()) as session:
        repository = ProfileRepository(session)
        if repository.count() > 100:
            raise SystemExit("Use a separate empty database: suite never removes existing profiles.")
        if not {p.user_id for p in repository.list()} <= {p.user_id for p in profiles[:100]}:
            raise SystemExit("Existing IDs are outside the demo seed; use a separate empty database.")
        previous = 0
        for size in (100, 1000, 10000, 25000, 50000):
            start = perf_counter()
            stats = dict(profiles_created=0, profiles_updated=0, embeddings_generated=0)
            for offset in range(previous, size, 500):
                repository.upsert_many(
                    profiles[offset : min(offset + 500, size)], get_matcher().embeddings, get_settings()
                )
                for key in stats:
                    stats[key] += repository.last_seed_stats[key]
                print(f"Seeded {min(offset + 500, size)}/{size}", flush=True)
            stats.update(network_size=size, seeding_time_seconds=round(perf_counter() - start, 3))
            reports.append(stats)
            Path("docs/scalability-seeding.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
            session.execute(text("ANALYZE professional_profiles"))
            session.commit()
            if repository.count() != size:
                raise RuntimeError("Network changed during the suite; benchmark size would be misleading")
            subprocess.run(
                [sys.executable, "scripts/benchmark_stored.py", "--output", f"docs/scalability-{size}.json"],
                check=True,
            )
            if size == 10000:
                subprocess.run([sys.executable, "scripts/evaluate_retrieval.py"], check=True)
            previous = size


if __name__ == "__main__":
    main()
