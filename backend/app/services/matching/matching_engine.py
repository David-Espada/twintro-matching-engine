from time import perf_counter

from app.core.constants import WEIGHTS
from app.schemas.matching import MatchMetadata, MatchResult, ProfileComparison, RelatedSkill, ScoreBreakdown
from app.schemas.profile import ProfessionalProfile
from app.services.embeddings.base import EmbeddingProvider
from app.services.matching.complementarity_engine import complementarity
from app.services.matching.connection_insight import connection_insight
from app.services.matching.experience_matcher import experience_score
from app.services.matching.industry_matcher import industry_score
from app.services.matching.interests_matcher import interests_score
from app.services.matching.role_matcher import role_score
from app.services.matching.scoring import complementarity_level, match_level, weighted_score
from app.services.matching.skills_matcher import concept_score, concept_similarity
from app.services.normalization.normalizer import canonical, normalize
from app.services.normalization.taxonomy import ROLE_COMPLEMENTS
from app.utils.timing import elapsed_ms


class MatchingEngine:
    def __init__(self, embeddings: EmbeddingProvider):
        self.embeddings = embeddings

    def prepare(self, profiles: list[ProfessionalProfile]) -> None:
        """Batch unique concepts before a ranking pass to avoid per-candidate inference."""
        concepts: set[str] = set()
        for profile in profiles:
            p = normalize(profile)
            concepts.update(p.skills + p.interests)
            concepts.update(v for v in (p.role, p.industry) if v)
        self.embeddings.encode(sorted(concepts))

    def compare(self, profile_a: ProfessionalProfile, profile_b: ProfessionalProfile) -> MatchResult:
        start = perf_counter()
        a, b = normalize(profile_a), normalize(profile_b)
        complement, strengths = complementarity(a, b)
        skill_matrix = (
            concept_similarity(a.skills, b.skills, self.embeddings) if a.skills and b.skills else None
        )
        scores = {
            "skills": concept_score(a.skills, b.skills, self.embeddings, matrix=skill_matrix),
            "role": role_score(a, b, self.embeddings),
            "industry": industry_score(a.industry, b.industry, self.embeddings),
            "experience": experience_score(profile_a.experience_years, profile_b.experience_years),
            "interests": interests_score(a.interests, b.interests, self.embeddings),
            "complementarity": complement,
        }
        available = sum(WEIGHTS[k] for k, v in scores.items() if v is not None)
        affinity = round(weighted_score(scores), 1)
        display_a = {canonical(s): s for s in profile_a.skills}
        display_b = {canonical(s): s for s in profile_b.skills}
        related: list[RelatedSkill] = []
        if a.skills and b.skills:
            matrix = skill_matrix
            for i, x in enumerate(a.skills):
                for j, y in enumerate(b.skills):
                    if x != y and matrix[i, j] >= 0.45:
                        related.append(
                            RelatedSkill(
                                source_skill=display_a[x],
                                target_skill=display_b[y],
                                similarity=round(float(matrix[i, j]) * 100, 1),
                            )
                        )
        related.sort(key=lambda r: (-r.similarity, r.source_skill, r.target_skill))
        complement_display = round(complement, 4) if complement is not None else None
        evidence_tags = []
        if set(a.skills) & set(b.skills):
            evidence_tags.append("Shared skills")
        if a.industry and a.industry == b.industry:
            evidence_tags.append("Same industry")
        if (a.family, b.family) in ROLE_COMPLEMENTS:
            evidence_tags.append("Complementary role")
        if related:
            evidence_tags.append("Semantic similarity")
        return MatchResult(
            source_user=profile_a,
            target_user=profile_b,
            affinity_percentage=affinity,
            match_level=match_level(affinity),
            complementarity_level=complementarity_level(complement_display),
            connection_insight=connection_insight(affinity, complement_display, available),
            target_role_family=b.family,
            target_normalized_industry=b.industry,
            evidence_tags=evidence_tags[:3],
            confidence=round(((a.completeness + b.completeness) / 2) * available, 3),
            score_breakdown=ScoreBreakdown(
                **{k: round(v, 4) if v is not None else None for k, v in scores.items()}
            ),
            profile_comparison=ProfileComparison(
                shared_domains=sorted(set(a.domains) & set(b.domains)),
                shared_skills=[display_a[s] for s in sorted(set(a.skills) & set(b.skills))],
                related_skills=related[:12],
                complementary_strengths=list(dict.fromkeys(strengths)),
            ),
            metadata=MatchMetadata(available_weight=round(available, 3), execution_time_ms=elapsed_ms(start)),
        )
