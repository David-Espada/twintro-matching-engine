from unittest.mock import MagicMock

import pytest
from app.api.dependencies import get_justification, get_matcher
from app.core.database import get_session
from app.main import app
from app.repositories.profile_repository import ProfileRepository
from app.services.embeddings.errors import EmbeddingUnavailableError
from app.services.justification.justification_service import JustificationService
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError


@pytest.fixture
def client(engine):
    app.dependency_overrides[get_matcher] = lambda: engine
    app.dependency_overrides[get_session] = lambda: MagicMock()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_api_match(client, engineer, product):
    response = client.post(
        "/api/v1/match/1-to-1", json={"profile_a": engineer.model_dump(), "profile_b": product.model_dump()}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["engine_version"] == "THDE-1.0"
    assert body["metadata"]["justification_provider"] == "template"
    assert body["justification"]
    for field in [
        "complementarity_level",
        "connection_insight",
        "score_breakdown",
        "profile_comparison",
        "affinity_percentage",
        "match_level",
        "confidence",
        "metadata",
    ]:
        assert field in body


def test_api_ranking_and_validation(client, engineer, product):
    payload = {
        "source_profile": engineer.model_dump(),
        "candidate_pool": [product.model_dump()],
        "justify_top": 0,
    }
    response = client.post("/api/v1/match/1-to-n", json=payload)
    assert response.status_code == 200
    assert response.json()["results"][0]["justification"] is None
    summary = response.json()["results"][0]
    assert summary["connection_insight"]
    assert summary["complementarity_level"]
    assert summary["target_role_family"] == "product"
    assert len(summary["evidence_tags"]) <= 3
    payload["limit"] = 0
    assert client.post("/api/v1/match/1-to-n", json=payload).status_code == 422
    payload["limit"] = 20
    payload["candidate_pool"] *= 2
    assert client.post("/api/v1/match/1-to-n", json=payload).status_code == 422


def test_demo_and_cors(client):
    assert len(client.get("/api/v1/profiles/demo").json()) >= 100
    response = client.options(
        "/api/v1/match/1-to-1",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_empty_candidate_pool_and_source_exclusion(client, engineer):
    for pool in ([], [engineer.model_dump()]):
        response = client.post(
            "/api/v1/match/1-to-n", json={"source_profile": engineer.model_dump(), "candidate_pool": pool}
        )
        assert response.status_code == 200
        assert response.json()["results"] == []
        assert response.json()["metadata"]["profiles_evaluated"] == 0


def test_database_unavailable_and_inline_resilience(client, engineer):
    session = MagicMock()
    failure = OperationalError("database offline", {}, Exception("connection failed"))
    session.scalar.side_effect = failure
    session.scalars.side_effect = failure
    session.commit.side_effect = failure
    app.dependency_overrides[get_session] = lambda: session
    response = client.get("/api/v1/profiles", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 503
    assert "Database unavailable" in response.json()["detail"]
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    request = {"source_profile": engineer.model_dump()}
    assert client.post("/api/v1/match/1-to-n", json=request).status_code == 503
    assert client.post("/api/v1/match/1-to-n", json=request | {"candidate_pool": []}).status_code == 200
    session.rollback.assert_called()


def test_vector_query_failure_never_claims_hybrid_success(client, engineer, monkeypatch):
    monkeypatch.setattr(ProfileRepository, "count", lambda *args, **kwargs: 50000)

    def fail(*args, **kwargs):
        raise OperationalError("vector query failed", {}, Exception("index unavailable"))

    monkeypatch.setattr(ProfileRepository, "hybrid_candidates", fail)
    response = client.post("/api/v1/match/1-to-n", json={"source_profile": engineer.model_dump()})
    assert response.status_code == 503
    assert "Database unavailable" in response.json()["detail"]
    assert "metadata" not in response.json()


def test_embedding_unavailable_has_clear_cors_error(client, engineer, monkeypatch, engine):
    def fail(*args):
        raise EmbeddingUnavailableError("Local embedding model unavailable. Check the model files.")

    monkeypatch.setattr(engine, "prepare", fail)
    response = client.post(
        "/api/v1/match/1-to-1",
        json={"profile_a": engineer.model_dump(), "profile_b": engineer.model_dump()},
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 503
    assert "Local embedding model unavailable" in response.json()["detail"]
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_openai_unavailable_never_breaks_api(client, engineer):
    broken = MagicMock()
    broken.explain.side_effect = RuntimeError("OpenAI unavailable")
    app.dependency_overrides[get_justification] = lambda: JustificationService(broken)
    response = client.post(
        "/api/v1/match/1-to-1", json={"profile_a": engineer.model_dump(), "profile_b": engineer.model_dump()}
    )
    assert response.status_code == 200
    assert response.json()["metadata"]["justification_provider"] == "template"
    assert response.json()["connection_insight"]


@pytest.mark.parametrize("change", [{"name": " "}, {"experience_years": -1}])
def test_invalid_profile_has_validation_error(client, engineer, change):
    response = client.post(
        "/api/v1/match/1-to-1",
        json={"profile_a": engineer.model_dump() | change, "profile_b": engineer.model_dump()},
    )
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
