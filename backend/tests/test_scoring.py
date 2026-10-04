import pytest
from app.services.matching.experience_matcher import experience_score
from app.services.matching.scoring import match_level, weighted_score


def test_formula():
    scores = dict(skills=90, role=80, industry=70, experience=60, interests=50, complementarity=40)
    assert weighted_score(scores) == pytest.approx(70.5)


def test_renormalization():
    assert weighted_score({"skills": 80, "interests": None}) == pytest.approx(80)
    assert weighted_score({"skills": None}) == 0


@pytest.mark.parametrize(
    "score,label",
    [
        (90, "Exceptional"),
        (89.9, "Strong"),
        (80, "Strong"),
        (70, "Good"),
        (60, "Moderate"),
        (40, "Low"),
        (39.9, "Weak"),
    ],
)
def test_levels(score, label):
    assert match_level(score) == f"{label} Match"


@pytest.mark.parametrize(
    "a,b,expected", [(0, 2.9, 100), (2, 3, 80), (0, 7, 60), (0, 12, 40), (0, 20, 25), (15, 80, 100)]
)
def test_experience(a, b, expected):
    assert experience_score(a, b) == expected


@pytest.mark.parametrize("value", [-1, 101, float("nan"), float("inf")])
def test_bad_component_rejected(value):
    with pytest.raises(ValueError):
        weighted_score({"skills": value})
