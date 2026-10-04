from unittest.mock import patch

import numpy as np
import pytest
from app.core.config import Settings
from app.repositories.profile_repository import ProfileRepository
from app.services.matching.skills_matcher import concept_similarity
from app.services.ranking.candidate_retrieval import retrieve_inline
from app.services.ranking.ranking_engine import RankingEngine
from app.services.ranking.retrieval_result import RetrievalResult
from sklearn.metrics.pairwise import cosine_similarity


@pytest.mark.parametrize("count,mode", [(2, "full"), (3, "full"), (4, "hybrid")])
def test_exact_threshold(engine, engineer, product, count, mode):
    candidates = [product.model_copy(update={"user_id": str(i)}) for i in range(count)]
    result = RankingEngine(engine, Settings(full_scan_threshold=3)).rank(engineer, [engineer, *candidates])
    assert result.metadata.retrieval_mode == mode
    assert result.metadata.total_network_size == count + 1
    assert all(r.target_user.user_id != engineer.user_id for r in result.results)


def test_union_and_every_candidate_uses_same_thde(engine, engineer, product):
    pool = [product.model_copy(update={"user_id": str(i)}) for i in range(4)]
    retrieval = RetrievalResult(pool[:3], ["0", "1"], ["1", "2"])
    ranking = RankingEngine(engine, Settings())
    full = ranking.rank(engineer, pool)
    with patch.object(engine, "compare", wraps=engine.compare) as compare:
        hybrid = ranking.rank(
            engineer,
            retrieval.candidates,
            limit=1,
            pool_size=50000,
            preselected=True,
            retrieval=retrieval,
            total_network_size=50001,
        )
        assert [call.args[1].user_id for call in compare.call_args_list] == ["0", "1", "2"]
    assert hybrid.results[0].score_breakdown == full.results[0].score_breakdown
    m = hybrid.metadata
    assert (
        m.total_network_size,
        m.semantic_candidates,
        m.complementarity_candidates,
        m.candidate_pool_size,
        m.profiles_fully_scored,
        m.ranking_limit,
    ) == (50001, 2, 2, 3, 3, 1)
    assert m.profiles_evaluated == m.profiles_fully_scored
    assert m.retrieval_backend == "pgvector"


def test_inline_retrieval_union_limits_source_and_duplicates(engine, engineer, product):
    settings = Settings(semantic_retrieval_limit=2, complementarity_retrieval_limit=3)
    pool = [product.model_copy(update={"user_id": str(i)}) for i in range(12)]
    result = retrieve_inline(engineer, [engineer, *pool, *pool], engine.embeddings, settings)
    ids = [p.user_id for p in result]
    assert len(ids) == len(set(ids)) <= 5
    assert engineer.user_id not in ids
    assert set(ids) == set(result.semantic_ids) | set(result.complementarity_ids)
    assert len(result.semantic_ids) == 2
    assert len(result.complementarity_ids) == 3


def test_empty_hybrid_result_retains_actual_backend_and_timings(engine, engineer):
    retrieval = RetrievalResult([], vector_retrieval_time_ms=12, complementarity_retrieval_time_ms=3)
    result = RankingEngine(engine, Settings()).rank(
        engineer, [], preselected=True, retrieval=retrieval, total_network_size=50000
    )
    assert result.results == []
    assert result.metadata.retrieval_backend == "pgvector"
    assert result.metadata.retrieval_mode == "hybrid"
    assert result.metadata.vector_retrieval_time_ms == 12
    assert result.metadata.complementarity_retrieval_time_ms == 3


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_cosine_optimization_matches_reference(dtype):
    rng = np.random.default_rng(42)
    values = rng.normal(size=(17, 384)).astype(dtype)
    values[0] = 0
    values[1] *= 1e-20

    class Provider:
        def encode(self, texts):
            return values.copy()

    actual = concept_similarity(tuple(map(str, range(7))), tuple(map(str, range(7, 17))), Provider())
    expected = np.clip(cosine_similarity(values[:7], values[7:]), 0, 1)
    np.testing.assert_allclose(actual, expected, atol=1e-7, rtol=1e-6)


@pytest.mark.parametrize(
    "vector,valid",
    [(None, False), ([0] * 384, False), ([1] * 383, False), ([float("nan")] * 384, False), ([1] * 384, True)],
)
def test_embedding_cache_requires_valid_current_dimensions(vector, valid):
    assert ProfileRepository.valid_embedding(vector, 384) is valid
