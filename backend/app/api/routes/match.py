from app.api.dependencies import get_justification, get_matcher
from app.core.config import get_settings
from app.core.database import get_session
from app.schemas.matching import MatchRequest, MatchResult, RankingRequest, RankingResult
from app.services.justification.justification_service import JustificationService
from app.services.matching.match_service import MatchService
from app.services.matching.matching_engine import MatchingEngine
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/match", tags=["matching"])


def get_service(
    session: Session = Depends(get_session),
    matcher: MatchingEngine = Depends(get_matcher),
    justification: JustificationService = Depends(get_justification),
) -> MatchService:
    return MatchService(matcher, justification, get_settings(), session)


@router.post("/1-to-1", response_model=MatchResult)
def compare_profiles(request: MatchRequest, service: MatchService = Depends(get_service)):
    return service.compare(request)


@router.post("/1-to-n", response_model=RankingResult)
def rank_profiles(request: RankingRequest, service: MatchService = Depends(get_service)):
    return service.rank(request)
