from app.core.constants import ENGINE_VERSION
from app.core.database import get_session
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

router = APIRouter(tags=["health"])


@router.get("/health")
def health(session: Session = Depends(get_session)):
    try:
        session.execute(text("SELECT 1 FROM professional_profiles LIMIT 1"))
        database = "connected"
    except SQLAlchemyError:
        session.rollback()
        database = "unavailable"
    return {
        "status": "ok" if database == "connected" else "degraded",
        "database": database,
        "engine_version": ENGINE_VERSION,
    }
