"""Presentation interpretation of completed scores; never feeds back into scoring."""

HIGH_SCORE_THRESHOLD = 80


def connection_insight(affinity: float, complementarity: float | None, available_weight: float) -> str:
    if available_weight == 0:
        return (
            "There is not enough profile evidence to assess professional affinity or collaboration potential."
        )
    if complementarity is None:
        return (
            "Affinity reflects the available matching dimensions. Add roles or recognized skill domains "
            "to assess collaboration potential separately."
        )
    high_affinity = affinity >= HIGH_SCORE_THRESHOLD
    high_complementarity = complementarity >= HIGH_SCORE_THRESHOLD
    if high_affinity and high_complementarity:
        return (
            "These professionals share a strong professional foundation and also bring "
            "complementary strengths."
        )
    if high_affinity:
        return (
            "These professionals are highly similar, making them suitable for peer collaboration, "
            "knowledge exchange, or comparable roles."
        )
    if high_complementarity:
        return (
            "These professionals work in different areas, but their capabilities may combine "
            "effectively in cross-functional collaboration."
        )
    return "The available profile evidence suggests limited professional alignment or complementary value."
