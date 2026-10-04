from app.schemas.profile import ProfessionalProfile


def test_identical_profiles(engine, engineer):
    result = engine.compare(engineer, engineer)
    assert result.affinity_percentage >= 90
    assert result.confidence == 1
    assert result.profile_comparison.shared_skills == ["FastAPI", "PostgreSQL", "Python"]


def test_unrelated_lower(engine, engineer):
    unrelated = ProfessionalProfile(
        user_id="u",
        name="Sam",
        role="Investment Analyst",
        industry="Finance",
        skills=["Valuation"],
        experience_years=20,
        interests=["Bonds"],
    )
    assert engine.compare(engineer, unrelated).affinity_percentage < 50


def test_identical_unclassified_profession(engine):
    profile = ProfessionalProfile(
        user_id="novel",
        name="Robin",
        role="Arborist",
        industry="Forestry",
        skills=["Tree care"],
        experience_years=5,
        interests=["Forest health"],
    )
    result = engine.compare(profile, profile)
    assert result.affinity_percentage >= 90
    assert result.score_breakdown.complementarity == 40


def test_determinism_and_symmetry(engine, engineer, product):
    first = engine.compare(engineer, product)
    for result in [engine.compare(engineer, product), engine.compare(product, engineer)]:
        assert result.affinity_percentage == first.affinity_percentage
        assert result.score_breakdown == first.score_breakdown
        assert result.confidence == first.confidence
        assert 0 <= result.affinity_percentage <= 100
        assert 0 <= result.confidence <= 1
