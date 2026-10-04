"""Full THDE top-K coverage of real pgvector+complementarity candidates on the SAME DB."""

import argparse
import json
from pathlib import Path
from statistics import mean

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.core.database import get_engine
from app.repositories.profile_repository import ProfileRepository
from app.services.ranking.ranking_engine import RankingEngine
from sqlalchemy.orm import Session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/retrieval-quality.json"))
    parser.add_argument("--max-network", type=int, default=10000)
    args = parser.parse_args()
    matcher, settings = get_matcher(), get_settings()
    rows = []
    with Session(get_engine()) as session:
        repository = ProfileRepository(session)
        count = repository.count()
        if count > args.max_network:
            raise SystemExit(
                f"Network has {count} rows; use a separate manageable database or explicitly raise --max-network."
            )
        pool = repository.list(limit=count)
        for uid in ("usr_00004", "usr_00084", "usr_00085", "usr_00086", "usr_00087", "usr_00088"):
            source = next(p for p in pool if p.user_id == uid)
            truth = RankingEngine(matcher, settings.model_copy(update={"full_scan_threshold": count})).rank(
                source, pool, limit=20
            )
            retrieved = repository.hybrid_candidates(source, matcher.embeddings, settings)
            ids = {p.user_id for p in retrieved}
            reranked = RankingEngine(matcher, settings).rank(
                source,
                retrieved.candidates,
                limit=20,
                pool_size=count - 1,
                preselected=True,
                retrieval=retrieved,
                total_network_size=count,
            )
            rows.append(
                {
                    "source_id": uid,
                    "role": source.role,
                    "candidate_pool_size": len(ids),
                    "semantic_candidates": len(retrieved.semantic_ids),
                    "complementarity_candidates": len(retrieved.complementarity_ids),
                    **{
                        f"recall@{k}": sum(r.target_user.user_id in ids for r in truth.results[:k])
                        / min(k, len(truth.results))
                        for k in (5, 10, 20)
                    },
                    "ground_truth_top20": [r.target_user.user_id for r in truth.results],
                    "retrieved_ids": sorted(ids),
                    "hybrid_top20": [r.target_user.user_id for r in reranked.results],
                }
            )
            print({k: v for k, v in rows[-1].items() if not isinstance(v, list)}, flush=True)
    report = {
        "network_size": count,
        "source_count": len(rows),
        "sources": rows,
        "average": {f"recall@{k}": mean(r[f"recall@{k}"] for r in rows) for k in (5, 10, 20)},
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(report["average"], flush=True)


if __name__ == "__main__":
    main()
