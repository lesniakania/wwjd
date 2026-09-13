"""Request-local retrieval traces and explicitly allowlisted evaluation metadata."""

import hashlib
import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

from .config import Settings
from .situation_analysis import SituationAnalysis


class RankedCandidate(BaseModel):
    reference: str
    quotation: str
    retrieval_score: float
    confidence: float


class RetrievalTrace(BaseModel):
    query: str = ""
    rerank_query: str = ""
    themes: dict[str, float] = Field(default_factory=dict)
    before_rerank: list[RankedCandidate] = Field(default_factory=list)
    after_rerank: list[RankedCandidate] = Field(default_factory=list)
    selected: list[str] = Field(default_factory=list)


class ReflectionDiagnostics(BaseModel):
    analysis: SituationAnalysis | None = None
    searches: list[RetrievalTrace] = Field(default_factory=list)
    configuration: dict[str, str | int | float | bool] = Field(default_factory=dict)


@lru_cache
def code_fingerprint() -> str:
    directory = Path(__file__).parent
    digest = hashlib.sha256()
    for path in sorted(directory.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def evaluation_configuration(settings: Settings) -> dict[str, str | int | float | bool]:
    return {
        "embedding_model": settings.embedding_model,
        "situation_analysis": settings.situation_analysis,
        "analysis_timeout_seconds": settings.analysis_timeout_seconds,
        "reranker_model": settings.reranker_model,
        "reranker_candidates": settings.reranker_candidates,
        "reranker_strategy": str(settings.reranker_strategy),
        "hf_model": settings.hf_model,
        "hf_model_pl": settings.hf_model_pl,
        "remote_generation_enabled": bool(settings.hf_token),
        "hf_max_tokens": settings.hf_max_tokens,
        "hf_timeout_seconds": settings.hf_timeout_seconds,
        "generation_temperature": 0.15,
        "code_sha256": code_fingerprint(),
        "commit": os.environ.get("SOURCE_COMMIT", os.environ.get("RENDER_GIT_COMMIT", "unknown")),
    }
