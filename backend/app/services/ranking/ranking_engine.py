from time import perf_counter

from app.core.config import Settings
from app.schemas.matching import RankingMetadata, RankingResult
from app.schemas.profile import ProfessionalProfile
from app.services.matching.matching_engine import MatchingEngine
from app.services.ranking.candidate_retrieval import retrieve_inline
from app.services.ranking.retrieval_result import RetrievalResult
from app.utils.timing import elapsed_ms


class RankingEngine:
    def __init__(self, matcher: MatchingEngine, settings: Settings):
        self.matcher = matcher
        self.settings = settings

    def rank(
        self,
        source: ProfessionalProfile,
        candidates: list[ProfessionalProfile],
        limit: int = 20,
        pool_size: int | None = None,
        preselected: bool = False,
        retrieval: RetrievalResult | None = None,
        total_network_size: int | None = None,
    ) -> RankingResult:
        start = perf_counter()
        network = len({p.user_id for p in candidates}) if total_network_size is None else total_network_size
        candidates = list({p.user_id: p for p in candidates if p.user_id != source.user_id}.values())
        total = len(candidates) if pool_size is None else pool_size
        hybrid = preselected or total > self.settings.full_scan_threshold
        if hybrid and not preselected:
            retrieval = retrieve_inline(source, candidates, self.matcher.embeddings, self.settings)
            candidates = retrieval.candidates
        if preselected and retrieval is None:
            raise ValueError("Preselected ranking requires actual retrieval metadata")
        score_start = perf_counter()
        if candidates:
            self.matcher.prepare([source, *candidates])
        results = [self.matcher.compare(source, p) for p in candidates]
        # Stable tie ordering, independent of input/database ordering.
        results.sort(key=lambda r: (-r.affinity_percentage, -r.confidence, r.target_user.user_id))
        for result in results:
            result.match_mode = "1-to-n"
        return RankingResult(
            source_user=source,
            results=results[:limit],
            metadata=RankingMetadata(
                profiles_evaluated=len(candidates),
                total_network_size=network,
                candidate_pool_size=len(candidates),
                profiles_fully_scored=len(results),
                semantic_candidates=len(retrieval.semantic_ids) if retrieval is not None else 0,
                complementarity_candidates=len(retrieval.complementarity_ids) if retrieval is not None else 0,
                retrieval_backend=retrieval.backend if retrieval is not None else "none",
                vector_retrieval_time_ms=retrieval.vector_retrieval_time_ms if retrieval is not None else 0,
                complementarity_retrieval_time_ms=retrieval.complementarity_retrieval_time_ms
                if retrieval is not None
                else 0,
                thde_scoring_time_ms=elapsed_ms(score_start),
                execution_time_ms=elapsed_ms(start),
                ranking_limit=limit,
                retrieval_mode="hybrid" if hybrid else "full",
            ),
        )
