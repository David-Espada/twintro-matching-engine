import json

from app.api.dependencies import get_matcher
from app.core.config import get_settings
from app.core.database import get_session
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfessionalProfile
from app.services.matching.matching_engine import MatchingEngine
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/demo", response_model=list[ProfessionalProfile])
def demo_profiles():
    return json.loads(get_settings().dataset_path.read_text(encoding="utf-8"))


@router.get("")
def list_profiles(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    repository = ProfileRepository(session)
    return {"items": repository.list(limit, offset), "total": repository.count()}


@router.post("", response_model=ProfessionalProfile)
def save_profile(
    profile: ProfessionalProfile,
    session: Session = Depends(get_session),
    matcher: MatchingEngine = Depends(get_matcher),
):
    ProfileRepository(session).upsert_many([profile], matcher.embeddings, get_settings())
    return profile


@router.get("/{user_id}", response_model=ProfessionalProfile)
def get_profile(user_id: str, session: Session = Depends(get_session)):
    profile = ProfileRepository(session).get(user_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile
