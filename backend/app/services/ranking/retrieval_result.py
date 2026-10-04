from dataclasses import dataclass, field

from app.schemas.profile import ProfessionalProfile


@dataclass
class RetrievalResult:
    candidates: list[ProfessionalProfile]
    semantic_ids: list[str] = field(default_factory=list)
    complementarity_ids: list[str] = field(default_factory=list)
    backend: str = "pgvector"
    vector_retrieval_time_ms: float = 0
    complementarity_retrieval_time_ms: float = 0

    def __iter__(self):
        return iter(self.candidates)

    def __bool__(self):
        return bool(self.candidates)
