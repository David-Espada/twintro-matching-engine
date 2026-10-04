from app.services.embeddings.base import EmbeddingProvider
from app.services.matching.skills_matcher import concept_similarity
from app.services.normalization.normalizer import NormalizedProfile
from app.services.normalization.taxonomy import ROLE_RELATIONS


def role_score(a: NormalizedProfile, b: NormalizedProfile, provider: EmbeddingProvider) -> float | None:
    if not a.role or not b.role:
        return None
    semantic = float(concept_similarity((a.role,), (b.role,), provider)[0, 0]) * 100
    # "other" is a bucket for unknowns, not evidence of a shared profession.
    family = (
        100
        if a.family == b.family != "other" or a.role == b.role
        else ROLE_RELATIONS.get((a.family, b.family), 20)
    )
    return 0.7 * semantic + 0.3 * family
