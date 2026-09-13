from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .context import ContextRegistry
from .generation import ReflectionGenerator
from .models import (
    HealthResponse,
    ReflectionRequest,
    ReflectionResponse,
    ShareCreatedResponse,
    SharedReflectionRequest,
    SharedReflectionResponse,
)
from .reflection_service import ReflectionService
from .retrieval import BgeReranker, Retriever, SemanticEncoder
from .retrieval_diagnostics import ReflectionDiagnostics, evaluation_configuration
from .share_repository import ShareRepository
from .situation_analysis import SituationAnalyzer
from .themes import SemanticThemeRouter


DATA_PATH = Path(__file__).parent / "data" / "web_verses.json"
DATA_PATH_PL = Path(__file__).parent / "data" / "polubg_verses.json"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    encoder = SemanticEncoder(settings.embedding_model) if settings.embedding_model else None
    reranker = BgeReranker(settings.reranker_model) if settings.reranker_model else None
    theme_router = SemanticThemeRouter(encoder) if encoder else None
    app.state.retrievers = {
        "en": Retriever(
            DATA_PATH,
            encoder,
            Retriever.cache_name(DATA_PATH, settings.embedding_model) if encoder else None,
            theme_router,
            reranker,
            settings.reranker_candidates,
            settings.reranker_strategy,
        ),
        "pl": Retriever(
            DATA_PATH_PL,
            encoder,
            Retriever.cache_name(DATA_PATH_PL, settings.embedding_model) if encoder else None,
            theme_router,
            reranker,
            settings.reranker_candidates,
            settings.reranker_strategy,
        ),
    }
    app.state.generator = ReflectionGenerator(settings)
    app.state.analyzer = SituationAnalyzer(settings)
    app.state.contexts = ContextRegistry()
    yield


app = FastAPI(
    title="What Would Jesus Do? API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    retriever: Retriever = request.app.state.retrievers["en"]
    generator: ReflectionGenerator = request.app.state.generator
    return HealthResponse(status="ok", verses=len(retriever.verses), generation_mode=generator.mode)


@app.post("/api/reflections", response_model=ReflectionResponse)
async def create_reflection(payload: ReflectionRequest, request: Request) -> ReflectionResponse:
    diagnostics = None
    if payload.diagnostics:
        if not get_settings().evaluation_diagnostics:
            raise HTTPException(status_code=403, detail="Evaluation diagnostics are disabled")
        diagnostics = ReflectionDiagnostics(
            configuration=evaluation_configuration(request.app.state.generator.settings)
        )
    service = ReflectionService(
        request.app.state.retrievers[payload.language],
        request.app.state.generator,
        request.app.state.contexts,
        request.app.state.analyzer,
    )
    return await service.create(payload.situation, payload.language, diagnostics)


@lru_cache
def _share_repository() -> ShareRepository:
    return ShareRepository(get_settings().database_url)


@app.post("/api/shares", response_model=ShareCreatedResponse, status_code=201)
async def create_share(payload: SharedReflectionRequest) -> ShareCreatedResponse:
    return ShareCreatedResponse(id=_share_repository().save(payload))


@app.get("/api/shares/{share_id}", response_model=SharedReflectionResponse)
async def get_share(share_id: str) -> SharedReflectionResponse:
    if len(share_id) > 64:
        raise HTTPException(status_code=404, detail="Shared reflection not found")
    shared_reflection = _share_repository().get(share_id)
    if shared_reflection is None:
        raise HTTPException(status_code=404, detail="Shared reflection not found")
    return SharedReflectionResponse(id=share_id, **shared_reflection.model_dump())
