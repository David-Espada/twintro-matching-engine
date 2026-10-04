from functools import lru_cache

from app.core.config import get_settings
from app.services.embeddings.sentence_transformer_provider import SentenceTransformerProvider
from app.services.justification.justification_service import JustificationService
from app.services.justification.openai_provider import OpenAIJustificationProvider
from app.services.matching.matching_engine import MatchingEngine


@lru_cache
def get_matcher() -> MatchingEngine:
    settings = get_settings()
    return MatchingEngine(
        SentenceTransformerProvider(
            settings.embedding_model, settings.embedding_dimensions, settings.embedding_cache_size
        )
    )


@lru_cache
def get_justification() -> JustificationService:
    settings = get_settings()
    provider = (
        OpenAIJustificationProvider(settings.openai_api_key, settings.openai_model)
        if settings.openai_api_key
        else None
    )
    return JustificationService(provider)
