import hashlib

import numpy as np
import pytest
from app.schemas.profile import ProfessionalProfile
from app.services.embeddings.base import EmbeddingProvider
from app.services.matching.matching_engine import MatchingEngine


class TestEmbeddings(EmbeddingProvider):
    """Stable orthogonal concept fixture; never used by the application."""

    def encode(self, texts):
        output = np.zeros((len(texts), 384), dtype=np.float32)
        for i, text in enumerate(texts):
            position = int(hashlib.sha256(text.encode()).hexdigest(), 16) % 384
            output[i, position] = 1
        return output


@pytest.fixture
def engine():
    return MatchingEngine(TestEmbeddings())


@pytest.fixture
def engineer():
    return ProfessionalProfile(
        user_id="eng",
        name="Alex Rivera",
        role="Backend Developer",
        industry="Technology",
        skills=["Python", "FastAPI", "PostgreSQL"],
        experience_years=8,
        interests=["Startups", "AI"],
    )


@pytest.fixture
def product():
    return ProfessionalProfile(
        user_id="pm",
        name="Morgan Chen",
        role="Product Manager",
        industry="Technology",
        skills=["Product strategy", "Roadmapping"],
        experience_years=7,
        interests=["Startups", "AI"],
    )
