from time import perf_counter

import numpy as np
from app.core.config import Settings
from app.schemas.profile import ProfessionalProfile
from app.services.embeddings.base import EmbeddingProvider
from app.services.matching.complementarity_engine import complementarity
from app.services.normalization.normalizer import normalize
from app.services.ranking.retrieval_result import RetrievalResult
from app.utils.timing import elapsed_ms


def retrieve_inline(
    source: ProfessionalProfile,
    candidates: list[ProfessionalProfile],
    embeddings: EmbeddingProvider,
    settings: Settings,
) -> RetrievalResult:
    """For an unpersisted pool, use the same hybrid union with in-memory vector search."""
    start = perf_counter()
    candidates = list({p.user_id: p for p in candidates if p.user_id != source.user_id}.values())
    a = normalize(source)
    normalized = [normalize(p) for p in candidates]
    vector = embeddings.encode([a.embedding_text()])[0]
    # Batch the full representations; concept inference is separately cached by the engine.
    similarities = []
    for start in range(0, len(normalized), 512):
        batch = embeddings.encode([p.embedding_text() for p in normalized[start : start + 512]])
        similarities.extend(np.clip(batch @ vector, -1, 1).tolist())
    semantic = sorted(range(len(candidates)), key=lambda i: (-similarities[i], candidates[i].user_id))
    vector_ms = elapsed_ms(start)
    start = perf_counter()
    complementary = sorted(
        range(len(candidates)),
        key=lambda i: (-(complementarity(a, normalized[i])[0] or 0), candidates[i].user_id),
    )
    selected = set(semantic[: settings.semantic_retrieval_limit]) | set(
        complementary[: settings.complementarity_retrieval_limit]
    )
    return RetrievalResult(
        candidates=[candidates[i] for i in sorted(selected)],
        semantic_ids=[candidates[i].user_id for i in semantic[: settings.semantic_retrieval_limit]],
        complementarity_ids=[
            candidates[i].user_id for i in complementary[: settings.complementarity_retrieval_limit]
        ],
        backend="numpy",
        vector_retrieval_time_ms=vector_ms,
        complementarity_retrieval_time_ms=elapsed_ms(start),
    )
