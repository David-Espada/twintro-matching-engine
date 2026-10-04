import math

from app.core.constants import WEIGHTS


def weighted_score(scores: dict[str, float | None], weights: dict[str, float] = WEIGHTS) -> float:
    available = [(score, weights[key]) for key, score in scores.items() if score is not None]
    if not available:
        return 0.0  # No evidence: confidence is also zero; not a measured incompatibility.
    if any(not math.isfinite(s) or not 0 <= s <= 100 for s, _ in available):
        raise ValueError("Component scores must be finite and between 0 and 100")
    return sum(s * w for s, w in available) / sum(w for _, w in available)


def match_level(score: float) -> str:
    for threshold, label in [
        (90, "Exceptional Match"),
        (80, "Strong Match"),
        (70, "Good Match"),
        (60, "Moderate Match"),
        (40, "Low Match"),
    ]:
        if score >= threshold:
            return label
    return "Weak Match"


def complementarity_level(score: float | None) -> str | None:
    """Classify the existing complementarity component without altering affinity."""
    if score is None:
        return None
    for threshold, label in [
        (90, "Exceptional"),
        (80, "Strong"),
        (70, "Good"),
        (60, "Moderate"),
        (40, "Low"),
    ]:
        if score >= threshold:
            return f"{label} Complementarity"
    return "Weak Complementarity"
