from app.services.embeddings.base import EmbeddingProvider
from app.services.matching.skills_matcher import concept_similarity
from app.services.normalization.taxonomy import INDUSTRY_RELATIONS


def industry_score(a: str | None, b: str | None, provider: EmbeddingProvider) -> float | None:
    if not a or not b:
        return None
    if a == b:
        return 100.0
    if (a, b) in INDUSTRY_RELATIONS:
        return INDUSTRY_RELATIONS[a, b]
    return float(concept_similarity((a,), (b,), provider)[0, 0]) * 100
