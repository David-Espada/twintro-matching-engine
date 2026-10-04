import pytest
from app.core.constants import WEIGHTS
from app.schemas.profile import ProfessionalProfile
from app.services.matching.connection_insight import connection_insight
from app.services.matching.scoring import complementarity_level, weighted_score


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, "Weak"),
        (39.9, "Weak"),
        (40, "Low"),
        (59.9, "Low"),
        (60, "Moderate"),
        (69.9, "Moderate"),
        (70, "Good"),
        (79.9, "Good"),
        (80, "Strong"),
        (89.9, "Strong"),
        (90, "Exceptional"),
        (100, "Exceptional"),
    ],
)
def test_complementarity_boundaries(score, expected):
    assert complementarity_level(score) == f"{expected} Complementarity"


@pytest.mark.parametrize(
    "affinity,complement,phrase",
    [
        (80, 80, "strong professional foundation"),
        (100, 79.9, "peer collaboration"),
        (79.9, 100, "cross-functional collaboration"),
        (0, 0, "limited professional alignment"),
    ],
)
def test_four_deterministic_insights(affinity, complement, phrase):
    first = connection_insight(affinity, complement, 1)
    assert phrase in first
    assert connection_insight(affinity, complement, 1) == first


def test_missing_evidence_does_not_claim_weak_complementarity(engine):
    empty = ProfessionalProfile(user_id="empty", name="Empty")
    result = engine.compare(empty, empty)
    assert complementarity_level(None) is None
    assert result.complementarity_level is None
    assert "not enough profile evidence" in result.connection_insight
    assert "Add roles" in connection_insight(100, None, 0.1)


def test_complementarity_is_not_affinity(engine, engineer, product):
    assert WEIGHTS == {
        "skills": 0.30,
        "role": 0.20,
        "industry": 0.15,
        "experience": 0.10,
        "interests": 0.10,
        "complementarity": 0.15,
    }
    result = engine.compare(engineer, product)
    assert result.score_breakdown.complementarity >= 90
    assert result.affinity_percentage < 80
    assert result.complementarity_level == "Exceptional Complementarity"
    assert "cross-functional" in result.connection_insight
    assert result.affinity_percentage == round(weighted_score(result.score_breakdown.model_dump()), 1)
    assert "Complementary role" in result.evidence_tags
    assert result.target_role_family == "product"
    assert len(result.evidence_tags) <= 3


def test_unknown_concepts_and_duplicate_concepts(engine):
    a = ProfessionalProfile(
        user_id="unknown",
        name="Robin",
        role="Arborist",
        industry="Forestry",
        skills=["Tree care", "tree care", " Tree care "],
        interests=["Urban forests", "urban forests"],
        experience_years=8,
    )
    b = a.model_copy(update={"user_id": "clean", "skills": ["Tree care"], "interests": ["Urban forests"]})
    result = engine.compare(a, b)
    assert result.target_role_family == "other"
    assert result.target_normalized_industry == "forestry"
    assert result.score_breakdown.skills == 100
    assert result.score_breakdown.interests == 100
    assert result.profile_comparison.shared_domains == []
    assert result.affinity_percentage == engine.compare(b, b).affinity_percentage
    assert 0 <= result.affinity_percentage <= 100
    assert 0 <= result.confidence <= 1
