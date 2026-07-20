from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .generation import LIMITATIONS_EN, LIMITATIONS_PL, ReflectionGenerator
from .localization import reference, translation_name
from .models import HealthResponse, ReflectionRequest, ReflectionResponse, Source
from .retrieval import Retriever
from .safety import check_safety


DATA_PATH = Path(__file__).parent / "data" / "web_verses.json"
DATA_PATH_PL = Path(__file__).parent / "data" / "polubg_verses.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.retrievers = {"en": Retriever(DATA_PATH), "pl": Retriever(DATA_PATH_PL)}
    app.state.generator = ReflectionGenerator(settings)
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
    safety = check_safety(payload.situation, payload.language)
    results = retriever.search(payload.situation, limit=5)
    if not results:
        results = retriever.search("wisdom love truth compassion", limit=5)
    generated = await generator.generate(payload.situation, results, payload.language)
    sources = [
        Source(
            reference=reference(
                result.passage.book,
                result.passage.chapter,
                result.passage.verse_start,
                result.passage.verse_end,
                payload.language,
            ),
            quotation=result.passage.text,
            translation=translation_name(payload.language),
            context_note=(
                ("Fragment jednej z czterech Ewangelii" if payload.language == "pl" else "From one of the four Gospels")
                if result.passage.book in {"Matthew", "Mark", "Luke", "John"}
                else ("Fragment wspierający z innej części Pisma" if payload.language == "pl" else "Supporting passage from elsewhere in Scripture")
            ),
        )
        for result in results[:4]
    ]
    return ReflectionResponse(
        summary=generated.summary,
        suggested_actions=generated.actions,
        sources=sources,
        safety_message=safety.message,
        limitations=LIMITATIONS_PL if payload.language == "pl" else LIMITATIONS_EN,
        generated_with=generated.mode,
    )
