import pytest
from app.core.constants import WEIGHTS
from app.schemas.profile import ProfessionalProfile
from app.services.matching.scoring import weighted_score
from app.services.normalization.normalizer import normalize


def test_missing_interests_are_not_zero(engine, engineer, product):
    product = product.model_copy(update={"interests": []})
    result = engine.compare(engineer, product)
    assert result.score_breakdown.interests is None
    assert result.metadata.available_weight == 0.9
    scores = result.score_breakdown.model_dump()
    assert result.affinity_percentage == round(weighted_score(scores), 1)
    zero_penalty = sum((v or 0) * WEIGHTS[k] for k, v in scores.items())
    assert result.affinity_percentage > zero_penalty
    assert result.confidence < 1


def test_empty_profiles_have_no_evidence(engine):
    profile = ProfessionalProfile(user_id="empty", name="Empty")
    result = engine.compare(profile, profile)
    assert result.affinity_percentage == 0
    assert result.confidence == 0
    assert all(v is None for v in result.score_breakdown.model_dump().values())


def test_zero_years_is_valid_evidence(engine, engineer):
    profile = engineer.model_copy(update={"experience_years": 0})
    assert engine.compare(profile, profile).confidence == 1


def test_normalization_preserves_display():
    p = ProfessionalProfile(
        user_id="a",
        name=" A ",
        role="Senior AI Engineer",
        industry="Tech",
        skills=[" ML ", "machine learning", "Python", "python"],
        interests=["AI", "ai"],
    )
    normalized = normalize(p)
    assert normalized.skills == ("machine learning", "python")
    assert normalized.interests == ("artificial intelligence",)
    assert normalized.family == "ai_data"
    assert normalized.industry == "technology"
    assert p.skills[0] == "ML"


@pytest.mark.parametrize("years", [-1, 81, float("nan"), float("inf")])
def test_invalid_experience(years):
    with pytest.raises(ValueError):
        ProfessionalProfile(user_id="x", name="X", experience_years=years)
