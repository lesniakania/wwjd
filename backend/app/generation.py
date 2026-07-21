import json
import re
from dataclasses import dataclass

import httpx

from .config import Settings
from .context import ContextCard
from .localization import Language, reference, relevance_note
from .retrieval import Retriever, SearchResult


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
            for _ in range(2):
                try:
                    return await self._generate_remote(situation, results, language, contexts or {})
                except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                    pass
            # A configured remote model is an enhancement, not a hard
            # dependency. Keep the endpoint available when the provider is
            # down or returns JSON that does not match the requested schema.
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
            "max_tokens": 1200,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.settings.hf_token}"}
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{self.settings.hf_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
        content = str(response.json()["choices"][0]["message"]["content"])
        data = self._parse_json_content(content)
        summary = self._plain_text(data["summary"])
        actions = [self._plain_text(action) for action in data["suggested_actions"]][:3]
        valid_ids = {
            Retriever.source_id(result.passage)
            for result in results
        }
        selected_sources = data.get("selected_sources", [])
        source_ids: tuple[str, ...] = ()
        applications: dict[str, str] = {}
        if isinstance(selected_sources, list):
            pairs = []
            for item in selected_sources[:3]:
                if not isinstance(item, dict):
                    continue
                source_id = self._canonical_source_id(str(item.get("id", "")), valid_ids)
                application = self._plain_text(item.get("situation_application", ""))
                if language == "pl" and self._has_unnatural_polish(application):
                    raise ValueError("Unnatural Polish application")
                pairs.append((source_id, application))
            source_ids = tuple(source_id for source_id, application in pairs if source_id in valid_ids and application)
            applications = {
                source_id: application
                for source_id, application in pairs
                if source_id in valid_ids and application
            }
        # Accept the previous shape during rolling deployments and from models
        # that imitate an earlier response found in their context.
        if not source_ids:
            source_ids = tuple(
                self._canonical_source_id(str(source_id), valid_ids)
                for source_id in data.get("selected_source_ids", [])[:3]
                if self._canonical_source_id(str(source_id), valid_ids)
            )
            raw_applications = data.get("source_explanations", {})
            if isinstance(raw_applications, dict):
                applications = {
                    source_id: str(raw_applications.get(source_id, "")).strip()
                    for source_id in source_ids
                    if str(raw_applications.get(source_id, "")).strip()
                }
        if not summary or not actions or not source_ids or len(applications) != len(source_ids):
            raise ValueError("Empty model response")
        return GeneratedReflection(
            summary,
            actions,
            f"hugging-face:{model}",
            source_ids,
            applications,
        )

    @staticmethod
    def _parse_json_content(content: str) -> dict:
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.removeprefix("```json").removeprefix("```")
            stripped = stripped.removesuffix("```").strip()
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            start, end = stripped.find("{"), stripped.rfind("}")
            if start < 0 or end <= start:
                raise
            parsed = json.loads(stripped[start : end + 1])
        if not isinstance(parsed, dict):
            raise ValueError("Model response is not a JSON object")
        return parsed

    @staticmethod
    def _plain_text(value: object) -> str:
        """Defensively remove common Markdown emphasis leaked by chat providers."""
        if isinstance(value, (list, tuple)):
            return " ".join(
                part
                for item in value
                if (part := ReflectionGenerator._plain_text(item))
            )
        text = str(value).strip()
        text = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda match: match.group(1) or match.group(2), text)
        return text.replace("`", "").strip()

    @staticmethod
    def _has_unnatural_polish(text: str) -> bool:
        lowered = text.lower()
        rejected = (
            "aplikacja ma ograniczenia",
            "powinien się wchodzić",
            "powinna się wchodzić",
            "powinni się wchodzić",
            "nieprzywilejowania się",
            "nieprzywilejować się",
        )
        return any(phrase in lowered for phrase in rejected)

    @staticmethod
    def _canonical_source_id(source_id: str, valid_ids: set[str]) -> str:
        if source_id in valid_ids:
            return source_id
        for valid_id in valid_ids:
            final_range = valid_id.rsplit(":", 1)[1]
            start, _, end = final_range.partition("-")
            if start == end and source_id == valid_id.removesuffix(f"-{end}"):
                return valid_id
        return ""

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
