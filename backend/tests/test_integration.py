"""Opt-in tests against the real local model and PostgreSQL; data changes are rolled back."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from app.api.dependencies import get_matcher
from app.core.config import Settings
from app.core.database import get_engine, initialize_database
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfessionalProfile
from app.services.matching.skills_matcher import concept_similarity
from app.services.ranking.ranking_engine import RankingEngine
from sqlalchemy.orm import Session

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("RUN_INTEGRATION") != "1",
        reason="Set RUN_INTEGRATION=1 with PostgreSQL and model available",
    ),
]


def test_real_semantic_concepts(engineer, product):
    matcher = get_matcher()
    pairs = [
        ("machine learning", "artificial intelligence"),
        ("fastapi", "backend development"),
        ("postgresql", "sql"),
        ("tensorflow", "deep learning"),
    ]
    for a, b in pairs:
        related = concept_similarity((a,), (b,), matcher.embeddings)[0, 0]
        unrelated = concept_similarity((a,), ("flower arranging",), matcher.embeddings)[0, 0]
        # MiniLM recognizes FastAPI only weakly; verify relative semantic evidence,
        # not an arbitrary absolute similarity threshold.
        assert related > unrelated + 0.05
    result = matcher.compare(engineer, engineer)
    assert result.affinity_percentage >= 90
    a = matcher.compare(engineer, product)
    b = matcher.compare(engineer, product)
    assert a.affinity_percentage == b.affinity_percentage
    assert a.score_breakdown == b.score_breakdown


def test_pgvector_cache_and_hybrid(engineer, product):
    initialize_database()
    settings = Settings()
    matcher = get_matcher()
    with get_engine().connect() as connection:
        transaction = connection.begin()
        try:
            with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
                repository = ProfileRepository(session)
                source = engineer.model_copy(update={"user_id": "integration_source"})
                target = product.model_copy(update={"user_id": "integration_target"})
                assert repository.upsert_many([source, target], matcher.embeddings, settings) == 2
                assert repository.last_seed_stats == {
                    "profiles_created": 2,
                    "profiles_updated": 0,
                    "embeddings_generated": 2,
                }
                assert repository.upsert_many([source, target], matcher.embeddings, settings) == 0
                assert repository.last_seed_stats == {
                    "profiles_created": 0,
                    "profiles_updated": 0,
                    "embeddings_generated": 0,
                }
                renamed = target.model_copy(update={"name": "Renamed professional"})
                assert repository.upsert_many([renamed], matcher.embeddings, settings) == 0
                assert repository.last_seed_stats["profiles_updated"] == 1
                assert repository.get(target.user_id).name == "Renamed professional"
                changed = target.model_copy(update={"skills": ["Figma"]})
                assert repository.upsert_many([changed], matcher.embeddings, settings) == 1
                # At 50k an arbitrary product profile need not make top 200/100.
                # An exact semantic clone provides an unambiguous retrieval fixture.
                clone = source.model_copy(update={"user_id": target.user_id})
                assert repository.upsert_many([clone], matcher.embeddings, settings) == 1
                results = repository.hybrid_candidates(source, matcher.embeddings, settings)
                ids = [p.user_id for p in results]
                assert target.user_id in ids
                assert source.user_id not in ids
                assert len(ids) == len(set(ids))
                # Unknown role and no domains still retrieve semantic neighbors without invalid SQL.
                unknown = source.model_copy(update={"role": None, "skills": []})
                assert repository.hybrid_candidates(unknown, matcher.embeddings, settings)
        finally:
            transaction.rollback()


def test_real_pgvector_union_metadata_and_thde_scoring():
    settings = Settings()
    matcher = get_matcher()
    with Session(get_engine()) as session:
        repository = ProfileRepository(session)
        source = repository.get("usr_00004")
        network = repository.count()
        if network < 1000:
            pytest.skip("Seed at least 1000 profiles to verify both retrieval limits")
        retrieved = repository.hybrid_candidates(source, matcher.embeddings, settings)
        ids = [p.user_id for p in retrieved]
        assert len(retrieved.semantic_ids) == 200
        assert len(retrieved.complementarity_ids) == 100
        assert len(ids) == len(set(ids)) <= 300
        assert set(ids) == set(retrieved.semantic_ids) | set(retrieved.complementarity_ids)
        assert source.user_id not in ids
        with patch.object(matcher, "compare", wraps=matcher.compare) as compare:
            result = RankingEngine(matcher, settings).rank(
                source,
                retrieved.candidates,
                limit=5,
                pool_size=network - 1,
                preselected=True,
                retrieval=retrieved,
                total_network_size=network,
            )
            assert {call.args[1].user_id for call in compare.call_args_list} == set(ids)
            assert compare.call_count == len(ids)
        assert result.metadata.profiles_fully_scored == len(ids)
        assert result.metadata.total_network_size == network
        for match in result.results:
            direct = matcher.compare(source, match.target_user)
            assert direct.affinity_percentage == match.affinity_percentage
            assert direct.score_breakdown == match.score_breakdown


@pytest.mark.parametrize(
    "aid,bid,minimum_affinity,maximum_affinity,minimum_complement,maximum_complement",
    [
        (81, 82, 90, 100, 0, 79.9),
        (81, 83, 80, 100, 0, 79.9),
        (4, 8, 0, 59.9, 90, 100),
        (85, 86, 60, 79.9, 80, 100),
        (87, 84, 70, 100, 80, 100),
        (88, 89, 0, 79.9, 80, 100),
        (81, 90, 0, 39.9, 0, 39.9),
        (91, 92, 60, 69.9, 0, 79.9),
        (81, 91, 70, 100, 80, 100),
    ],
)
def test_real_demo_relationships(
    aid, bid, minimum_affinity, maximum_affinity, minimum_complement, maximum_complement
):
    path = Path(__file__).resolve().parents[2] / "dataset/professional_profiles.json"
    profiles = {
        p["user_id"]: ProfessionalProfile.model_validate(p)
        for p in json.loads(path.read_text(encoding="utf-8"))
    }
    result = get_matcher().compare(profiles[f"usr_{aid:05d}"], profiles[f"usr_{bid:05d}"])
    assert minimum_affinity <= result.affinity_percentage <= maximum_affinity
    assert minimum_complement <= result.score_breakdown.complementarity <= maximum_complement
