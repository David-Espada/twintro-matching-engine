from __future__ import annotations

import hashlib
from time import perf_counter

import numpy as np
from app.core.config import Settings
from app.models.profile import ProfessionalProfileRow as Row
from app.schemas.profile import ProfessionalProfile
from app.services.embeddings.base import EmbeddingProvider
from app.services.normalization.normalizer import normalize
from app.services.normalization.taxonomy import DOMAIN_COMPLEMENTS, ROLE_COMPLEMENTS
from app.services.ranking.retrieval_result import RetrievalResult
from app.utils.timing import elapsed_ms
from sqlalchemy import case, func, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, defer


def to_profile(row: Row) -> ProfessionalProfile:
    return ProfessionalProfile(**{key: getattr(row, key) for key in ProfessionalProfile.model_fields})


class ProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self, exclude: str | None = None) -> int:
        query = select(func.count()).select_from(Row)
        if exclude:
            query = query.where(Row.user_id != exclude)
        return self.session.scalar(query) or 0

    def list(
        self, limit: int = 100, offset: int = 0, exclude: str | None = None
    ) -> list[ProfessionalProfile]:
        query = select(Row).options(defer(Row.embedding)).order_by(Row.user_id).limit(limit).offset(offset)
        if exclude:
            query = query.where(Row.user_id != exclude)
        return [to_profile(row) for row in self.session.scalars(query)]

    def get(self, user_id: str) -> ProfessionalProfile | None:
        row = self.session.scalar(select(Row).where(Row.user_id == user_id))
        return to_profile(row) if row else None

    def upsert_many(
        self, profiles: list[ProfessionalProfile], embeddings: EmbeddingProvider, settings: Settings
    ) -> int:
        """Skip inference when the canonical representation and model fingerprint are unchanged."""
        normalized = [normalize(p) for p in profiles]
        existing = {
            r.user_id: r
            for r in self.session.scalars(select(Row).where(Row.user_id.in_([p.user_id for p in profiles])))
        }
        hashes = {
            p.original.user_id: hashlib.sha256(
                (settings.embedding_model + "\n" + p.embedding_text()).encode()
            ).hexdigest()
            for p in normalized
        }
        changed = [
            p
            for p in normalized
            if p.original.user_id not in existing
            or existing[p.original.user_id].embedding_hash != hashes[p.original.user_id]
            or existing[p.original.user_id].embedding_model != settings.embedding_model
            or not self.valid_embedding(existing[p.original.user_id].embedding, settings.embedding_dimensions)
        ]
        vectors = embeddings.encode([p.embedding_text() for p in changed])
        encoded = {p.original.user_id: vector.tolist() for p, vector in zip(changed, vectors, strict=True)}
        rows = []
        for p in normalized:
            uid = p.original.user_id
            values = p.original.model_dump() | dict(
                normalized_role=p.role,
                normalized_industry=p.industry,
                role_family=p.family,
                skill_domains=list(p.domains),
                embedding_model=settings.embedding_model,
                embedding_hash=hashes[uid],
                embedding=encoded[uid] if uid in encoded else existing[uid].embedding,
            )
            rows.append(values)
        if rows:
            statement = insert(Row).values(rows)
            self.session.execute(
                statement.on_conflict_do_update(
                    index_elements=[Row.user_id],
                    set_={key: getattr(statement.excluded, key) for key in rows[0]}
                    | {"updated_at": func.now()},
                )
            )
        self.last_seed_stats = {
            "profiles_created": sum(p.user_id not in existing for p in profiles),
            "profiles_updated": sum(
                p.user_id in existing
                and any(getattr(existing[p.user_id], k) != v for k, v in p.model_dump().items())
                for p in profiles
            ),
            "embeddings_generated": len(changed),
        }
        self.session.commit()
        return len(changed)

    @staticmethod
    def valid_embedding(vector, dimensions: int) -> bool:
        return (
            vector is not None
            and len(vector) == dimensions
            and bool(np.isfinite(vector).all())
            and bool(np.any(vector))
        )

    def configure_vector_search(self, settings: Settings) -> None:
        # Transaction-local settings cannot leak to pooled connections.
        self.session.execute(
            text("SELECT set_config('hnsw.ef_search', :depth, true)"),
            {"depth": str(min(1000, max(400, settings.semantic_retrieval_limit * 2)))},
        )
        self.session.execute(text("SET LOCAL hnsw.iterative_scan = strict_order"))

    def semantic_query(self, source: ProfessionalProfile, vector: list[float], settings: Settings):
        return (
            select(Row)
            .options(defer(Row.embedding))
            .where(Row.user_id != source.user_id, Row.embedding_model == settings.embedding_model)
            .order_by(Row.embedding.cosine_distance(vector))
            .limit(settings.semantic_retrieval_limit)
        )

    def hybrid_candidates(
        self, source: ProfessionalProfile, embeddings: EmbeddingProvider, settings: Settings
    ) -> RetrievalResult:
        start = perf_counter()
        a = normalize(source)
        vector = embeddings.encode([a.embedding_text()])[0].tolist()
        self.configure_vector_search(settings)
        semantic = self.session.scalars(self.semantic_query(source, vector, settings)).all()
        vector_ms = elapsed_ms(start)
        start = perf_counter()
        role_cases = [
            (Row.role_family == family, score)
            for (origin, family), score in ROLE_COMPLEMENTS.items()
            if origin == a.family
        ]
        domain_cases = [
            (Row.skill_domains.contains([target]), score)
            for (origin, target), score in DOMAIN_COMPLEMENTS.items()
            if origin in a.domains
        ]
        role_value = case(*role_cases, else_=0) if role_cases else 0
        domain_value = (
            func.greatest(0, *[case((condition, value), else_=0) for condition, value in domain_cases])
            if domain_cases
            else 0
        )
        strength = role_value * 0.7 + domain_value * 0.3
        # SQL expressions select useful relationships only; unrelated difference adds no retrieval value.
        if not role_cases and not domain_cases:
            complementary = []
        else:
            complementary = self.session.scalars(
                select(Row)
                .options(defer(Row.embedding))
                .where(Row.user_id != source.user_id, strength > 0)
                .order_by(strength.desc(), Row.user_id)
                .limit(settings.complementarity_retrieval_limit)
            ).all()
        return RetrievalResult(
            candidates=[
                to_profile(row) for row in {r.user_id: r for r in [*semantic, *complementary]}.values()
            ],
            semantic_ids=[r.user_id for r in semantic],
            complementarity_ids=[r.user_id for r in complementary],
            vector_retrieval_time_ms=vector_ms,
            complementarity_retrieval_time_ms=elapsed_ms(start),
        )
