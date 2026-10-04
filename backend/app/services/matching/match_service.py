import logging
from time import perf_counter

from app.core.config import Settings
from app.core.constants import ENGINE_VERSION
from app.models.match_result import MatchHistory
from app.repositories.profile_repository import ProfileRepository
from app.schemas.matching import MatchRequest, MatchResult, RankingRequest, RankingResult
from app.services.justification.justification_service import JustificationService
from app.services.matching.matching_engine import MatchingEngine
from app.services.ranking.ranking_engine import RankingEngine
from app.utils.timing import elapsed_ms
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MatchService:
    def __init__(
        self,
        matcher: MatchingEngine,
        justification: JustificationService,
        settings: Settings,
        session: Session,
    ):
        self.matcher, self.justification, self.settings, self.session = (
            matcher,
            justification,
            settings,
            session,
        )

    def _record(self, result: MatchResult | RankingResult) -> None:
        try:
            self.session.add(
                MatchHistory(
                    match_mode=result.match_mode,
                    source_user_id=result.source_user.user_id,
                    engine_version=ENGINE_VERSION,
                    result=result.model_dump(mode="json"),
                )
            )
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            logger.warning("Match history could not be persisted; inline matching remains available")

    def compare(self, request: MatchRequest) -> MatchResult:
        start = perf_counter()
        self.matcher.prepare([request.profile_a, request.profile_b])
        result = self.matcher.compare(request.profile_a, request.profile_b)
        self.justification.apply(result)
        result.metadata.execution_time_ms = elapsed_ms(start)
        self._record(result)
        result.metadata.execution_time_ms = elapsed_ms(start)
        return result

    def rank(self, request: RankingRequest) -> RankingResult:
        start = perf_counter()
        candidates = request.candidate_pool
        count, preselected = None, False
        retrieval, network_size = None, None
        if candidates is None:
            repository = ProfileRepository(self.session)
            network_size = repository.count()
            count = repository.count(exclude=request.source_profile.user_id)
            preselected = count > self.settings.full_scan_threshold
            if preselected:
                retrieval = repository.hybrid_candidates(
                    request.source_profile, self.matcher.embeddings, self.settings
                )
                candidates = retrieval.candidates
            else:
                candidates = repository.list(
                    limit=self.settings.full_scan_threshold, exclude=request.source_profile.user_id
                )
        result = RankingEngine(self.matcher, self.settings).rank(
            request.source_profile,
            candidates,
            request.limit,
            count,
            preselected,
            retrieval=retrieval,
            total_network_size=network_size,
        )
        for match in result.results[: request.justify_top]:
            self.justification.apply(match)
        result.metadata.execution_time_ms = elapsed_ms(start)
        self._record(result)
        result.metadata.execution_time_ms = elapsed_ms(start)
        return result
