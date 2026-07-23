import json
import logging
from time import perf_counter
from dataclasses import dataclass

import httpx

from .config import Settings
from .context import ContextCard
from .localization import Language, reference, relevance_note
from .model_response import ModelResponseParser
from .retrieval import Retriever, SearchResult


logger = logging.getLogger(__name__)


LIMITATIONS_EN = (
    "This is an AI-generated, Bible-grounded reflection—not a certain declaration of what Jesus "
    "would do, and not a substitute for pastoral, medical, legal, or mental-health advice."
)
LIMITATIONS_PL = (
    "To wygenerowana przez AI refleksja oparta na Biblii, a nie pewne stwierdzenie, co zrobiłby "
    "Jezus. Nie zastępuje porady duszpasterskiej, medycznej, prawnej ani psychologicznej."
)


@dataclass(frozen=True)
class GeneratedReflection:
    summary: str
    actions: list[str]
    mode: str
    source_ids: tuple[str, ...]
    applications: dict[str, str]


SYSTEM_PROMPT = """You write a cautious, compassionate Bible-grounded reflection.
Use only the supplied passages as scriptural evidence. Do not add Bible references or quotations.
Never claim certainty about what Jesus would do. Distinguish an application from the passage itself.
Do not advise secrecy, retaliation, or remaining in danger. Professional and emergency help take priority.
Write natural, idiomatic prose in the requested language. In Polish, proofread every sentence for correct
case, agreement, and inflection before returning it. Use plain text only: never use Markdown, asterisks,
headings, or emphasis markers in any JSON string.
The supplied reviewed context cards are the only source of facts about a passage. Do not reconstruct,
expand, correct, or repeat their historical and literary claims. Write only the modern application.
Select only 1-3 of the supplied candidate passages. Prefer fewer passages when another candidate adds
little, is only indirectly related, or requires a strained application. For every selected passage, write
a natural situation_application of 1-3 sentences explaining why its reviewed original meaning is relevant
and where that application has limits. Return strict JSON with keys: summary (2-4 sentences),
suggested_actions (1-3 short strings), and selected_sources (an array of 1-3 objects). Every selected source
object must contain exactly these string fields: id and situation_application.
The situation_application must contain exactly two short sentences. State the connection directly in the
first sentence. In the second, give a natural qualification beginning with "Nie oznacza to jednak, że..."
in Polish or "This does not mean that..." in English. Never refer to the text as "aplikacja", "application",
"powyższy fragment", or "the above passage". Prefer ordinary verbs and concrete language. In Polish write
"wchodzić w konflikt", never "się wchodzić w konflikt"; write "nie ulegać fałszywym informacjom", never
"nieprzywilejować się wobec informacji"."""


class ReflectionGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def mode(self) -> str:
        return "hugging-face" if self.settings.hf_token else "local-extractive"

    def model_for(self, language: Language) -> str:
        return self.settings.hf_model_pl if language == "pl" else self.settings.hf_model

    async def generate(
        self, situation: str, results: list[SearchResult], language: Language,
        contexts: dict[str, ContextCard] | None = None,
    ) -> GeneratedReflection:
        if self.settings.hf_token:
            for attempt in range(1, 3):
                started = perf_counter()
                try:
                    generated = await self._generate_remote(
                        situation, results, language, contexts or {}
                    )
                    logger.info(
                        "reflection_model completed duration_ms=%.1f attempt=%d model=%s",
                        (perf_counter() - started) * 1000,
                        attempt,
                        self.model_for(language),
                    )
                    return generated
                except httpx.HTTPStatusError as exc:
                    retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
                    logger.warning(
                        "reflection_model failed duration_ms=%.1f attempt=%d model=%s "
                        "status_code=%d retryable=%s",
                        (perf_counter() - started) * 1000,
                        attempt,
                        self.model_for(language),
                        exc.response.status_code,
                        retryable,
                    )
                    if not retryable or attempt == 2:
                        break
                except httpx.TransportError:
                    logger.warning(
                        "reflection_model failed duration_ms=%.1f attempt=%d model=%s "
                        "error=transport retryable=true",
                        (perf_counter() - started) * 1000,
                        attempt,
                        self.model_for(language),
                    )
                    if attempt == 2:
                        break
                except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                    logger.warning(
                        "reflection_model failed duration_ms=%.1f attempt=%d model=%s "
                        "error=invalid_response retryable=%s",
                        (perf_counter() - started) * 1000,
                        attempt,
                        self.model_for(language),
                        attempt == 1,
                    )
                    if attempt == 2:
                        break
            # A configured remote model is an enhancement, not a hard
            # dependency. Keep the endpoint available when the provider is
            # down or returns JSON that does not match the requested schema.
            logger.warning(
                "reflection_model using_local_fallback model=%s candidate_count=%d",
                self.model_for(language),
                len(results),
            )
            return self._generate_local(results, language)
        return self._generate_local(results, language)

    async def _generate_remote(
        self, situation: str, results: list[SearchResult], language: Language,
        contexts: dict[str, ContextCard],
    ) -> GeneratedReflection:
        blocks = []
        for result in results:
            source_id = Retriever.source_id(result.passage)
            card = contexts[source_id]
            blocks.append(
                f"[ID {source_id}] Selected verse: {result.passage.reference}: {result.passage.text}\n"
                f"Reviewed context: {card.origin_context} {card.broader_context}\n"
                f"Reviewed original meaning: {card.original_meaning}"
            )
        passages = "\n".join(blocks)
        language_instruction = "Write in Polish." if language == "pl" else "Write in English."
        user_prompt = (
            f"{language_instruction}\nSituation:\n{situation}\n\nSupplied passages:\n{passages}"
        )
        model = self.model_for(language)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.15,
            "max_tokens": self.settings.hf_max_tokens,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.settings.hf_token}"}
        async with httpx.AsyncClient(timeout=self.settings.hf_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.hf_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        content = str(response.json()["choices"][0]["message"]["content"])
        valid_ids = {Retriever.source_id(result.passage) for result in results}
        parsed = ModelResponseParser(valid_ids).parse(content, language)
        return GeneratedReflection(
            parsed.summary,
            parsed.actions,
            f"hugging-face:{model}",
            parsed.source_ids,
            parsed.applications,
        )

    @staticmethod
    def _parse_json_content(content: str) -> dict:
        return ModelResponseParser._parse_json(content)

    @staticmethod
    def _plain_text(value: object) -> str:
        return ModelResponseParser.plain_text(value)

    @staticmethod
    def _has_unnatural_polish(text: str) -> bool:
        return ModelResponseParser.has_unnatural_polish(text)

    @staticmethod
    def _canonical_source_id(source_id: str, valid_ids: set[str]) -> str:
        return ModelResponseParser(valid_ids).canonical_source_id(source_id)

    @staticmethod
    def _generate_local(results: list[SearchResult], language: Language) -> GeneratedReflection:
        selected_results = results[:2]
        primary = selected_results[0].passage
        secondary = selected_results[1].passage if len(selected_results) > 1 else None
        primary_reference = reference(
            primary.book, primary.chapter, primary.verse_start, primary.verse_end, language
        )
        secondary_reference = (
            reference(
                secondary.book, secondary.chapter, secondary.verse_start, secondary.verse_end, language
            )
            if secondary
            else None
        )
        if language == "pl":
            summary = (
                f"Biblijna droga zaczyna się od zasady wyrażonej w {primary_reference}. Spójrz na "
                "sytuację uczciwie i ze współczuciem dla każdej osoby, a następnie wybierz działanie "
                "zgodne z odnalezionym nauczaniem — nie traktując tej refleksji jako pewnej odpowiedzi."
            )
            actions = [
                f"Przeczytaj {primary_reference} w kontekście całego rozdziału przed podjęciem decyzji.",
                "Oddziel znane fakty od przypuszczeń i wybierz najbardziej prawdomówny oraz pełen miłości następny krok.",
            ]
            if secondary_reference:
                actions.append(f"Porównaj to zastosowanie z perspektywą w {secondary_reference}.")
            applications = {
                Retriever.source_id(result.passage): relevance_note(result.themes, language)
                for result in selected_results
            }
            return GeneratedReflection(
                summary, actions[:3], "local-extractive", tuple(applications), applications
            )
        summary = (
            f"A Bible-grounded approach begins with the principle expressed in {primary_reference}. "
            "Consider the situation honestly, with compassion for everyone affected, and choose an "
            "action consistent with the retrieved teaching rather than treating this as a certain answer."
        )
        actions = [
            f"Read {primary_reference} in its full chapter before deciding.",
            "Separate the known facts from assumptions, then choose the most truthful and loving next step.",
        ]
        if secondary:
            actions.append(f"Compare that application with the perspective in {secondary_reference}.")
        applications = {
            Retriever.source_id(result.passage): relevance_note(result.themes, language)
            for result in selected_results
        }
        return GeneratedReflection(
            summary, actions[:3], "local-extractive", tuple(applications), applications
        )
