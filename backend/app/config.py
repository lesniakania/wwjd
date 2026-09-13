from functools import lru_cache

from pydantic import Field

from .retrieval_models import RerankerStrategy

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    hf_token: str = ""
    hf_model: str = "Qwen/Qwen3-4B-Instruct-2507"
    hf_model_pl: str = "speakleash/Bielik-11B-v3.0-Instruct"
    hf_base_url: str = "https://router.huggingface.co/v1"
    hf_max_tokens: int = 1200
    hf_timeout_seconds: float = 45.0
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    max_situation_length: int = 3000
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_candidates: int = Field(default=50, ge=6, le=500)
    reranker_strategy: RerankerStrategy = RerankerStrategy.RAW
    situation_analysis: bool = False
    analysis_timeout_seconds: float = Field(default=20, gt=0, le=120)
    evaluation_diagnostics: bool = False
    database_url: str = "postgresql://wwjd:secret@localhost:5434/wwjd"

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
