import logging
from collections.abc import Mapping
from time import perf_counter

from .context import ContextCard, ContextRegistry
from .generation import LIMITATIONS_EN, LIMITATIONS_PL, ReflectionGenerator
from .localization import Language, reference, relevance_note, translation_name
from .models import ReflectionResponse, Source
from .retrieval import Retriever, SearchResult
from .safety import check_safety


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
            context_sources=list(context.context_sources),
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
    ):
        self.retriever = retriever
        self.generator = generator
        self.contexts = contexts
        self.source_factory = SourceFactory(retriever)

    async def create(self, situation: str, language: Language) -> ReflectionResponse:
        safety = check_safety(situation, language)
        results = self._retrieve(situation, language)
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
        )

    def _retrieve(self, situation: str, language: Language) -> list[SearchResult]:
        retrieval_started = perf_counter()
        results = self.retriever.search(situation, limit=6)
        if not results:
            results = self.retriever.search(FALLBACK_QUERIES[language], limit=3)
        logger.info(
            "reflection_retrieval completed duration_ms=%.1f language=%s result_count=%d",
            (perf_counter() - retrieval_started) * 1000,
            language,
            len(results),
        )
        return results
