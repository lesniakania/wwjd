from contextlib import asynccontextmanager
import logging
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .context import ContextRegistry
from .generation import LIMITATIONS_EN, LIMITATIONS_PL, ReflectionGenerator
from .localization import reference, relevance_note, translation_name
from .models import HealthResponse, ReflectionRequest, ReflectionResponse, Source
from .retrieval import Retriever, SemanticEncoder
from .safety import check_safety


logger = logging.getLogger(__name__)


DATA_PATH = Path(__file__).parent / "data" / "web_verses.json"
DATA_PATH_PL = Path(__file__).parent / "data" / "polubg_verses.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    encoder = SemanticEncoder(settings.embedding_model) if settings.embedding_model else None
    app.state.retrievers = {
        "en": Retriever(
            DATA_PATH,
            encoder,
            Retriever.cache_name(DATA_PATH, settings.embedding_model) if encoder else None,
        ),
        "pl": Retriever(
            DATA_PATH_PL,
            encoder,
            Retriever.cache_name(DATA_PATH_PL, settings.embedding_model) if encoder else None,
        ),
    }
    app.state.generator = ReflectionGenerator(settings)
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
    retriever: Retriever = request.app.state.retrievers[payload.language]
    generator: ReflectionGenerator = request.app.state.generator
    context_registry: ContextRegistry = request.app.state.contexts
    safety = check_safety(payload.situation, payload.language)
    retrieval_started = perf_counter()
    results = retriever.search(payload.situation, limit=6)
    if not results:
        fallback = (
            "mądrość miłość prawda współczucie" if payload.language == "pl"
            else "wisdom love truth compassion"
        )
        results = retriever.search(fallback, limit=3)
    logger.info(
        "reflection_retrieval completed duration_ms=%.1f language=%s result_count=%d",
        (perf_counter() - retrieval_started) * 1000,
        payload.language,
        len(results),
    )
    contexts = {
        Retriever.source_id(result.passage): context_registry.for_passage(result.passage, payload.language)
        for result in results
    }
    generated = await generator.generate(payload.situation, results, payload.language, contexts)
    result_by_id = {Retriever.source_id(result.passage): result for result in results}
    selected_results = [
        result_by_id[source_id]
        for source_id in generated.source_ids
        if source_id in result_by_id
    ]
    sources = _sources_from_results(
        selected_results, payload.language, generated.applications, contexts, retriever
    )
    return ReflectionResponse(
        summary=generated.summary,
        suggested_actions=generated.actions,
        sources=sources,
        safety_message=safety.message,
        limitations=LIMITATIONS_PL if payload.language == "pl" else LIMITATIONS_EN,
        generated_with=generated.mode,
    )


def _sources_from_results(results, language, applications, contexts, retriever):
    return [
        Source(
            reference=reference(
                result.passage.book,
                result.passage.chapter,
                result.passage.verse_start,
                result.passage.verse_end,
            language,
            ),
            quotation=result.passage.text,
            literary_type=contexts[Retriever.source_id(result.passage)].literary_type,
            origin_context=contexts[Retriever.source_id(result.passage)].origin_context,
            broader_context=contexts[Retriever.source_id(result.passage)].broader_context,
            original_meaning=contexts[Retriever.source_id(result.passage)].original_meaning,
            situation_application=applications[Retriever.source_id(result.passage)],
            context_sources=list(contexts[Retriever.source_id(result.passage)].context_sources),
            context_confidence=contexts[Retriever.source_id(result.passage)].confidence,
            context_reviewed=contexts[Retriever.source_id(result.passage)].reviewed,
            translation=translation_name(language),
            context_note=(
                ("Fragment jednej z czterech Ewangelii" if language == "pl" else "From one of the four Gospels")
                if result.passage.book in {"Matthew", "Mark", "Luke", "John"}
                else ("Fragment wspierający z innej części Pisma" if language == "pl" else "Supporting passage from elsewhere in Scripture")
            ),
            relevance=relevance_note(result.themes, language),
            context_reference=reference(
                contexts[Retriever.source_id(result.passage)].book,
                contexts[Retriever.source_id(result.passage)].context_chapter,
                contexts[Retriever.source_id(result.passage)].context_verse_start,
                contexts[Retriever.source_id(result.passage)].context_verse_end,
                language,
            ),
            context_quotation=retriever.passage_range(
                contexts[Retriever.source_id(result.passage)].book,
                contexts[Retriever.source_id(result.passage)].context_chapter,
                contexts[Retriever.source_id(result.passage)].context_verse_start,
                contexts[Retriever.source_id(result.passage)].context_verse_end,
            ).text,
        )
        for result in results
    ]
