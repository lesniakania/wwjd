import logging
from collections.abc import Mapping
from time import perf_counter

from .context import ContextCard, ContextRegistry
from .context_sources import context_source
from .generation import LIMITATIONS_EN, LIMITATIONS_PL, ReflectionGenerator
from .localization import Language, reference, relevance_note, translation_name
from .models import ReflectionResponse, Source
from .retrieval import Retriever, SearchResult
from .retrieval_diagnostics import ReflectionDiagnostics, RetrievalTrace
from .safety import check_safety
from .situation_analysis import SituationAnalyzer


logger = logging.getLogger(__name__)

FALLBACK_QUERIES: dict[Language, str] = {
    "pl": "mądrość miłość prawda współczucie",
    "en": "wisdom love truth compassion",
}


class SourceFactory:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def create_all(
        self,
        results: list[SearchResult],
        language: Language,
        applications: Mapping[str, str],
        contexts: Mapping[str, ContextCard],
    ) -> list[Source]:
        return [
            self._create(result, language, applications, contexts)
            for result in results
        ]

    def _create(
        self,
        result: SearchResult,
        language: Language,
        applications: Mapping[str, str],
        contexts: Mapping[str, ContextCard],
    ) -> Source:
        source_id = Retriever.source_id(result.passage)
        context = contexts[source_id]
        return Source(
            reference=reference(
                result.passage.book,
                result.passage.chapter,
                result.passage.verse_start,
                result.passage.verse_end,
                language,
            ),
            quotation=result.passage.text,
            literary_type=context.literary_type,
            origin_context=context.origin_context,
            broader_context=context.broader_context,
            original_meaning=context.original_meaning,
            situation_application=applications[source_id],
            context_sources=[
                context_source(label, language) for label in context.context_sources
            ],
            context_confidence=context.confidence,
            context_reviewed=context.reviewed,
            translation=translation_name(language),
            context_note=self._context_note(result.passage.book, language),
            relevance=relevance_note(result.themes, language),
            context_reference=reference(
                context.book,
                context.context_chapter,
                context.context_verse_start,
                context.context_verse_end,
                language,
            ),
            context_quotation=self.retriever.passage_range(
                context.book,
                context.context_chapter,
                context.context_verse_start,
                context.context_verse_end,
            ).text,
        )

    @staticmethod
    def _context_note(book: str, language: Language) -> str:
        is_gospel = book in {"Matthew", "Mark", "Luke", "John"}
        if language == "pl":
            return (
                "Fragment jednej z czterech Ewangelii"
                if is_gospel
                else "Fragment wspierający z innej części Pisma"
            )
        return (
            "From one of the four Gospels"
            if is_gospel
            else "Supporting passage from elsewhere in Scripture"
        )


class ReflectionService:
    def __init__(
        self,
        retriever: Retriever,
        generator: ReflectionGenerator,
        contexts: ContextRegistry,
        analyzer: SituationAnalyzer | None = None,
    ):
        self.retriever = retriever
        self.generator = generator
        self.contexts = contexts
        self.source_factory = SourceFactory(retriever)
        self.analyzer = analyzer

    async def create(
        self, situation: str, language: Language,
        diagnostics: ReflectionDiagnostics | None = None,
    ) -> ReflectionResponse:
        safety = check_safety(situation, language)
        query = situation
        theme_override = None
        if self.analyzer is not None:
            analysis = await self.analyzer.analyze(situation, language)
            if diagnostics is not None:
                diagnostics.analysis = analysis
            if analysis.profile is not None:
                query = analysis.profile.search_query
                theme_override = {
                    str(theme): 0.95 - rank * 0.05
                    for rank, theme in enumerate(analysis.profile.themes)
                }
        results = self._retrieve(query, language, diagnostics, theme_override)
        contexts = {
            Retriever.source_id(result.passage): self.contexts.for_passage(
                result.passage, language
            )
            for result in results
        }
        generated = await self.generator.generate(situation, results, language, contexts)
        result_by_id = {
            Retriever.source_id(result.passage): result for result in results
        }
        selected_results = [
            result_by_id[source_id]
            for source_id in generated.source_ids
            if source_id in result_by_id
        ]
        sources = self.source_factory.create_all(
            selected_results,
            language,
            generated.applications,
            contexts,
        )
        limitations = LIMITATIONS_PL if language == "pl" else LIMITATIONS_EN
        return ReflectionResponse(
            summary=generated.summary,
            suggested_actions=generated.actions,
            sources=sources,
            safety_message=safety.message,
            limitations=limitations,
            generated_with=generated.mode,
            diagnostics=diagnostics,
        )

    def _retrieve(
        self, situation: str, language: Language,
        diagnostics: ReflectionDiagnostics | None = None,
        theme_override: dict[str, float] | None = None,
    ) -> list[SearchResult]:
        retrieval_started = perf_counter()
        overrides = {} if theme_override is None else {"theme_override": theme_override}
        if diagnostics is None:
            results = self.retriever.search(situation, limit=6, **overrides)
        else:
            trace = RetrievalTrace()
            results = self.retriever.search(situation, limit=6, trace=trace, **overrides)
            diagnostics.searches.append(trace)
        if not results:
            if diagnostics is None:
                results = self.retriever.search(FALLBACK_QUERIES[language], limit=3)
            else:
                trace = RetrievalTrace()
                results = self.retriever.search(FALLBACK_QUERIES[language], limit=3, trace=trace)
                diagnostics.searches.append(trace)
        logger.info(
            "reflection_retrieval completed duration_ms=%.1f language=%s result_count=%d",
            (perf_counter() - retrieval_started) * 1000,
            language,
            len(results),
        )
        return results
