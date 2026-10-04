from datetime import datetime

from app.core.config import get_settings
from app.core.database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, Index, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column


class ProfessionalProfileRow(Base):
    __tablename__ = "professional_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    role: Mapped[str | None] = mapped_column(String(200))
    normalized_role: Mapped[str | None] = mapped_column(String(200))
    role_family: Mapped[str] = mapped_column(String(50), index=True)
    industry: Mapped[str | None] = mapped_column(String(150))
    normalized_industry: Mapped[str | None] = mapped_column(String(150))
    skills: Mapped[list] = mapped_column(JSONB)
    skill_domains: Mapped[list[str]] = mapped_column(ARRAY(String))
    interests: Mapped[list] = mapped_column(JSONB)
    experience_years: Mapped[float | None] = mapped_column(Float)
    professional_summary: Mapped[str | None]
    embedding: Mapped[list[float]] = mapped_column(Vector(get_settings().embedding_dimensions))
    embedding_model: Mapped[str] = mapped_column(String(200))
    embedding_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    __table_args__ = (
        Index(
            "ix_profiles_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("ix_profiles_skill_domains", "skill_domains", postgresql_using="gin"),
    )
