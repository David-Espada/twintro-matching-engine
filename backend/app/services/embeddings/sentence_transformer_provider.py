import logging
from collections import OrderedDict
from collections.abc import Sequence
from threading import RLock

import numpy as np
from app.services.embeddings.base import EmbeddingProvider
from app.services.embeddings.errors import EmbeddingUnavailableError


class SentenceTransformerProvider(EmbeddingProvider):
    """Local CPU inference with batched encoding and a bounded, thread-safe concept cache."""

    def __init__(self, model_name: str, dimensions: int = 384, cache_size: int = 50000):
        self.model_name = model_name
        self.dimensions = dimensions
        self.cache_size = cache_size
        self._model = None
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._lock = RLock()

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        try:
            return self._encode(texts)
        except Exception as error:
            logging.getLogger(__name__).exception("Local embedding inference failed")
            raise EmbeddingUnavailableError(
                "Local embedding model unavailable. Check the model files, model configuration, "
                "and internet access for the first download, then retry."
            ) from error

    def _encode(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimensions), dtype=np.float32)
        with self._lock:
            if self._model is None:
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer(self.model_name, device="cpu")
                model.eval()
                if model.get_sentence_embedding_dimension() != self.dimensions:
                    raise ValueError("Embedding model dimensions do not match EMBEDDING_DIMENSIONS")
                self._model = model
            missing = sorted(set(texts) - self._cache.keys())
            fresh = {}
            if missing:
                vectors = self._model.encode(
                    missing,
                    batch_size=128,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                )
                fresh = dict(zip(missing, vectors, strict=True))
            result = np.stack([fresh[t] if t in fresh else self._cache[t] for t in texts])
            self._cache.update(fresh)
            for text in texts:
                self._cache.move_to_end(text)
            while len(self._cache) > self.cache_size:
                self._cache.popitem(last=False)
            return result
