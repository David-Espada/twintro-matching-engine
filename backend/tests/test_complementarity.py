from app.services.matching.complementarity_engine import complementarity
from app.services.normalization.normalizer import normalize
from app.services.normalization.taxonomy import DOMAIN_COMPLEMENTS, ROLE_COMPLEMENTS


def test_professionally_useful_differences(engine, engineer, product):
    result = engine.compare(engineer, product)
    assert result.score_breakdown.complementarity >= 90
    assert not result.profile_comparison.shared_skills
    assert result.profile_comparison.complementary_strengths


def test_matrices_are_symmetric():
    for matrix in [ROLE_COMPLEMENTS, DOMAIN_COMPLEMENTS]:
        for (a, b), score in matrix.items():
            assert matrix[b, a] == score


def test_missing_domains_reweight_role(engineer, product):
    a = normalize(engineer.model_copy(update={"skills": []}))
    b = normalize(product)
    assert complementarity(a, b)[0] == 95
