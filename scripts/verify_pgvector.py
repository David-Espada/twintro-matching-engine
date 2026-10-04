"""Capture actual catalogs and EXPLAIN ANALYZE for the production semantic query."""

import json
from pathlib import Path

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.core.database import get_engine
from app.repositories.profile_repository import ProfileRepository
from app.services.normalization.normalizer import normalize
from sqlalchemy import text
from sqlalchemy.orm import Session


def main():
    with Session(get_engine()) as session:
        repository = ProfileRepository(session)
        settings = get_settings()
        source = repository.get("usr_00004")
        vector = get_matcher().embeddings.encode([normalize(source).embedding_text()])[0].tolist()
        query = repository.semantic_query(source, vector, settings)
        sql = str(query.compile(session.bind, compile_kwargs={"literal_binds": True}))
        report = {
            "extension_version": session.scalar(
                text("SELECT extversion FROM pg_extension WHERE extname='vector'")
            ),
            "column_type": session.scalar(
                text(
                    "SELECT format_type(atttypid, atttypmod) FROM pg_attribute WHERE attrelid='professional_profiles'::regclass AND attname='embedding'"
                )
            ),
            "vectors": [
                dict(r)
                for r in session.execute(
                    text(
                        "SELECT count(*) AS count, min(vector_dims(embedding)) AS min_dimensions, max(vector_dims(embedding)) AS max_dimensions, embedding_model FROM professional_profiles GROUP BY embedding_model"
                    )
                ).mappings()
            ],
            "indexes": list(
                session.scalars(
                    text("SELECT indexdef FROM pg_indexes WHERE tablename='professional_profiles'")
                )
            ),
        }
        # Baseline settings from the audited implementation, followed by current settings.
        for name, depth, iterative in [("audited_defaults", 40, "off"), ("production", 400, "strict_order")]:
            session.execute(text("SELECT set_config('hnsw.ef_search', :depth, true)"), {"depth": str(depth)})
            session.execute(
                text("SELECT set_config('hnsw.iterative_scan', :mode, true)"), {"mode": iterative}
            )
            plan = session.scalar(text("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + sql))
            report[name] = {"ef_search": depth, "iterative_scan": iterative, "plan": plan}
        Path("docs/pgvector-verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        for name in ("audited_defaults", "production"):
            plan = report[name]["plan"][0]
            print(
                name,
                "rows",
                plan["Plan"]["Actual Rows"],
                "ms",
                plan["Execution Time"],
                "index used",
                "ix_profiles_embedding_hnsw" in json.dumps(plan),
            )


if __name__ == "__main__":
    main()
