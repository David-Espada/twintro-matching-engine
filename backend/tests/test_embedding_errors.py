import pytest
from app.services.embeddings.errors import EmbeddingUnavailableError
from app.services.embeddings.sentence_transformer_provider import SentenceTransformerProvider


def test_provider_errors_are_actionable(monkeypatch):
    provider = SentenceTransformerProvider("unavailable")

    def fail(_):
        raise OSError("missing weights")

    monkeypatch.setattr(provider, "_encode", fail)
    with pytest.raises(EmbeddingUnavailableError, match="Local embedding model unavailable"):
        provider.encode(["python"])
