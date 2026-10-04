"""Measure actual PostgreSQL ranking; fresh process cold, then warm model/cache."""

import argparse
import json
from pathlib import Path

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.core.database import get_engine
from app.repositories.profile_repository import ProfileRepository
from app.schemas.matching import RankingRequest
from app.services.justification.justification_service import JustificationService
from app.services.matching.match_service import MatchService
from sqlalchemy.orm import Session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reports = []
    with Session(get_engine()) as session:
        source = ProfileRepository(session).get("usr_00004")
        service = MatchService(get_matcher(), JustificationService(), get_settings(), session)
        for run in ("cold", "warm"):
            result = service.rank(RankingRequest(source_profile=source, limit=5, justify_top=0))
            reports.append(
                {
                    "run": run,
                    **result.metadata.model_dump(),
                    "source": source.model_dump(),
                    "top5": [
                        {
                            "user_id": r.target_user.user_id,
                            "name": r.target_user.name,
                            "role": r.target_user.role,
                            "affinity": r.affinity_percentage,
                            "complementarity": r.score_breakdown.complementarity,
                        }
                        for r in result.results
                    ],
                }
            )
    args.output.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(
        json.dumps([{k: v for k, v in r.items() if k not in ("source", "top5")} for r in reports]), flush=True
    )


if __name__ == "__main__":
    main()
