from abc import ABC, abstractmethod

from app.schemas.matching import MatchResult


class JustificationProvider(ABC):
    name: str

    @abstractmethod
    def explain(self, result: MatchResult) -> str:
        raise NotImplementedError
