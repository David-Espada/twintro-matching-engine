def experience_band(years: float) -> int:
    """Continuous intervals: [0,3), [3,6), [6,10), [10,15), [15,infinity)."""
    return sum(years >= cutoff for cutoff in (3, 6, 10, 15))


def experience_score(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return float((100, 80, 60, 40, 25)[abs(experience_band(a) - experience_band(b))])
