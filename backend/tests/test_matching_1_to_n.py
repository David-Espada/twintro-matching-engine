from app.core.config import Settings
from app.services.ranking.ranking_engine import RankingEngine


def test_ranking(engine, engineer, product):
    clone = engineer.model_copy(update={"user_id": "clone"})
    result = RankingEngine(engine, Settings()).rank(engineer, [product, engineer, clone])
    assert result.results[0].target_user.user_id == "clone"
    scores = [r.affinity_percentage for r in result.results]
    assert scores == sorted(scores, reverse=True)
    assert result.metadata.profiles_evaluated == 2
    assert result.metadata.candidate_pool_size == 2


def test_hybrid_union_deduplicates(engine, engineer, product):
    settings = Settings(full_scan_threshold=2, semantic_retrieval_limit=2, complementarity_retrieval_limit=2)
    candidates = [product.model_copy(update={"user_id": f"pm{i}"}) for i in range(5)]
    result = RankingEngine(engine, settings).rank(engineer, candidates, limit=1)
    assert result.metadata.retrieval_mode == "hybrid"
    assert result.metadata.total_network_size == 5
    assert result.metadata.candidate_pool_size == result.metadata.profiles_fully_scored
    assert result.metadata.retrieval_backend == "numpy"
    assert result.metadata.profiles_evaluated <= 4
    assert len(result.results) == 1


def test_tie_breaks_and_empty_pool(engine, engineer, product):
    ranking = RankingEngine(engine, Settings())
    pool = [product.model_copy(update={"user_id": str(i)}) for i in range(3)]

    def ids(ps):
        return [r.target_user.user_id for r in ranking.rank(engineer, ps).results]

    assert ids(pool) == ids(list(reversed(pool)))
    assert ranking.rank(engineer, []).results == []


def test_empty_pool_does_not_require_embedding_model(engine, engineer, monkeypatch):
    def fail(*args):
        raise AssertionError("An empty pool needs no semantic inference")

    monkeypatch.setattr(engine, "prepare", fail)
    assert RankingEngine(engine, Settings()).rank(engineer, []).results == []
