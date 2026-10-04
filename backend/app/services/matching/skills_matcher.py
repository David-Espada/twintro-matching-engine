import numpy as np
from app.services.embeddings.base import EmbeddingProvider


def concept_similarity(a: tuple[str, ...], b: tuple[str, ...], provider: EmbeddingProvider) -> np.ndarray:
    vectors = provider.encode(list(a) + list(b))
    # Providers supply dense finite arrays. Match sklearn's L2 normalization,
    # including its near-zero guard, without repeated generic dataframe validation.
    norms = np.sqrt(np.einsum("ij,ij->i", vectors, vectors))
    norms[norms < 10 * np.finfo(vectors.dtype).eps] = 1
    normalized = vectors / norms[:, None]
    return np.clip(normalized[: len(a)] @ normalized[len(a) :].T, 0, 1)


def concept_score(
    a: tuple[str, ...],
    b: tuple[str, ...],
    provider: EmbeddingProvider,
    matrix: np.ndarray | None = None,
) -> float | None:
    """Jaccard exact overlap plus symmetric mean best-concept cosine similarity."""
    if not a or not b:
        return None
    exact = len(set(a) & set(b)) / len(set(a) | set(b))
    if matrix is None:
        matrix = concept_similarity(a, b, provider)
    semantic = float((matrix.max(axis=1).mean() + matrix.max(axis=0).mean()) / 2)
    return min(100.0, 100 * (0.4 * exact + 0.6 * semantic))
