from datetime import datetime

from app.core.database import Base
from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class MatchHistory(Base):
    __tablename__ = "match_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    match_mode: Mapped[str] = mapped_column(String(10))
    source_user_id: Mapped[str] = mapped_column(String(100), index=True)
    engine_version: Mapped[str] = mapped_column(String(30))
    result: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
