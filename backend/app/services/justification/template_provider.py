from app.schemas.matching import MatchResult
from app.services.justification.base import JustificationProvider


class TemplateJustificationProvider(JustificationProvider):
    name = "template"

    def explain(self, result: MatchResult) -> str:
        if result.metadata.available_weight == 0:
            return "There is not enough professional information to assess compatibility. Add roles, skills, and interests."
        comparison = result.profile_comparison
        sentences = [
            f"{result.source_user.name} and {result.target_user.name} have a "
            f"{result.match_level.lower()} ({result.affinity_percentage:.1f}% affinity)."
        ]
        if result.score_breakdown.complementarity is not None:
            sentences.append(
                f"Collaboration potential is {result.score_breakdown.complementarity:.1f}% "
                f"({result.complementarity_level.lower()}); it is distinct from overall affinity."
            )
        if comparison.shared_skills:
            sentences.append(f"Shared skills include {', '.join(comparison.shared_skills[:3])}.")
        if comparison.complementary_strengths:
            sentences.append(f"Explore collaboration across {comparison.complementary_strengths[0]}.")
        if not comparison.shared_skills and not comparison.complementary_strengths:
            sentences.append("Discuss project goals to establish whether collaboration would be useful.")
        if result.confidence < 0.8:
            sentences.append("Some profile information is missing; complete it to improve confidence.")
        return " ".join(sentences)
