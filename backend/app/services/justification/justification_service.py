import logging

from app.schemas.matching import MatchResult
from app.services.justification.base import JustificationProvider
from app.services.justification.template_provider import TemplateJustificationProvider

logger = logging.getLogger(__name__)


class JustificationService:
    def __init__(self, optional_provider: JustificationProvider | None = None):
        self.optional_provider = optional_provider
        self.fallback = TemplateJustificationProvider()

    def apply(self, result: MatchResult) -> None:
        provider = self.optional_provider or self.fallback
        try:
            explanation = provider.explain(result.model_copy(deep=True))
            if not isinstance(explanation, str) or not explanation.strip():
                raise ValueError("Explanation provider returned no text")
        except Exception:
            logger.warning("Optional justification provider failed; using deterministic template")
            provider = self.fallback
            explanation = provider.explain(result)
        result.justification = explanation
        result.metadata.justification_provider = provider.name
