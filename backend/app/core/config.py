from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(ROOT / ".env", ".env"), extra="ignore")
    database_url: str = "postgresql+psycopg://twintro:twintro@localhost:5433/twintro"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    dataset_path: Path = ROOT / "dataset/professional_profiles.json"
    embedding_dimensions: int = Field(default=384, ge=1)
    embedding_cache_size: int = Field(default=50000, ge=1000)
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    cors_origins: list[str] = ["http://localhost:3000"]
    full_scan_threshold: int = Field(default=10000, ge=1)
    semantic_retrieval_limit: int = Field(default=200, ge=1)
    complementarity_retrieval_limit: int = Field(default=100, ge=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
