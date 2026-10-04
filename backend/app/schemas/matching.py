from typing import Literal

from app.core.constants import ENGINE_VERSION
from app.schemas.profile import ProfessionalProfile
from pydantic import BaseModel, Field, model_validator


class MatchRequest(BaseModel):
    profile_a: ProfessionalProfile
    profile_b: ProfessionalProfile


class RankingRequest(BaseModel):
    source_profile: ProfessionalProfile
    candidate_pool: list[ProfessionalProfile] | None = Field(default=None, max_length=50000)
    limit: int = Field(default=20, ge=1, le=100)
    justify_top: int = Field(default=5, ge=0, le=100)

    @model_validator(mode="after")
    def unique_candidates(self) -> "RankingRequest":
        if self.candidate_pool is not None:
            ids = [p.user_id for p in self.candidate_pool]
            if len(ids) != len(set(ids)):
                raise ValueError("candidate_pool must contain unique user_id values")
        return self


class ScoreBreakdown(BaseModel):
    skills: float | None
    role: float | None
    industry: float | None
    experience: float | None
    interests: float | None
    complementarity: float | None


class RelatedSkill(BaseModel):
    source_skill: str
    target_skill: str
    similarity: float


class ProfileComparison(BaseModel):
    shared_domains: list[str]
    shared_skills: list[str]
    related_skills: list[RelatedSkill]
    complementary_strengths: list[str]


class MatchMetadata(BaseModel):
    execution_time_ms: float = 0
    engine_version: str = ENGINE_VERSION
    available_weight: float
    justification_provider: str = "none"


class MatchResult(BaseModel):
    match_mode: Literal["1-to-1", "1-to-n"] = "1-to-1"
    source_user: ProfessionalProfile
    target_user: ProfessionalProfile
    affinity_percentage: float = Field(ge=0, le=100)
    match_level: str
    complementarity_level: str | None
    connection_insight: str
    target_role_family: str
    target_normalized_industry: str | None
    evidence_tags: list[str]
    confidence: float = Field(ge=0, le=1)
    score_breakdown: ScoreBreakdown
    profile_comparison: ProfileComparison
    justification: str | None = None
    metadata: MatchMetadata


class RankingMetadata(BaseModel):
    profiles_evaluated: int
    total_network_size: int
    semantic_candidates: int = 0
    complementarity_candidates: int = 0
    candidate_pool_size: int
    profiles_fully_scored: int
    retrieval_backend: Literal["none", "pgvector", "numpy"] = "none"
    vector_retrieval_time_ms: float = 0
    complementarity_retrieval_time_ms: float = 0
    thde_scoring_time_ms: float = 0
    execution_time_ms: float
    ranking_limit: int
    retrieval_mode: Literal["full", "hybrid"]
    engine_version: str = ENGINE_VERSION


class RankingResult(BaseModel):
    match_mode: Literal["1-to-n"] = "1-to-n"
    source_user: ProfessionalProfile
    results: list[MatchResult]
    metadata: RankingMetadata
