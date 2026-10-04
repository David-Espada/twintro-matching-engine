from abc import ABC, abstractmethod
from collections.abc import Sequence

import numpy as np


class EmbeddingProvider(ABC):
    """Providers return finite, normalized vectors in a stable order."""

    @abstractmethod
    def encode(self, texts: Sequence[str]) -> np.ndarray:
        raise NotImplementedError
