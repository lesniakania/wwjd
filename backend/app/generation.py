import json
from dataclasses import dataclass

import httpx

from .config import Settings
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
    explanations: dict[str, str]


SYSTEM_PROMPT = """You write a cautious, compassionate Bible-grounded reflection.
Use only the supplied passages as scriptural evidence. Do not add Bible references or quotations.
Never claim certainty about what Jesus would do. Distinguish an application from the passage itself.
Do not advise secrecy, retaliation, or remaining in danger. Professional and emergency help take priority.
Explain the connection between the situation and the supplied passages; do not merely summarize them.
Select only 1-3 of the supplied candidate passages. Prefer fewer passages when another candidate adds
little, is only indirectly related, or requires a strained application. For every selected passage, write
a clear explanation of exactly four substantive sentences in this order: (1) who is speaking or writing and
to whom, (2) the immediate narrative or argumentative situation, (3) the passage's original main point, and
(4) why that point is relevant here and the limit of that application. If the supplied context does not
establish one of those facts, say so briefly rather than inventing it. Explicitly distinguish original meaning from modern
application. Return strict JSON with keys: summary (2-4 sentences), suggested_actions (1-3 short strings),
and selected_sources (an array of 1-3 objects). Every selected source object must contain exactly these
string fields: id, speaker_and_audience, immediate_context, original_meaning, and situation_application."""


class ReflectionGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def mode(self) -> str:
        return "hugging-face" if self.settings.hf_token else "local-extractive"

    async def generate(
        self, situation: str, results: list[SearchResult], language: Language
    ) -> GeneratedReflection:
        if self.settings.hf_token:
            for _ in range(2):
                try:
                    return await self._generate_remote(situation, results, language)
                except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                    pass
            # A configured remote model is an enhancement, not a hard
            # dependency. Keep the endpoint available when the provider is
            # down or returns JSON that does not match the requested schema.
            return self._generate_local(results, language)
        return self._generate_local(results, language)

    async def _generate_remote(
        self, situation: str, results: list[SearchResult], language: Language
    ) -> GeneratedReflection:
        passages = "\n".join(
            f"[ID {result.passage.book}:{result.passage.chapter}:{result.passage.verse_start}-{result.passage.verse_end}] "
            f"Selected verse: {result.passage.reference}: {result.passage.text}\n"
            f"Context: {result.context.reference}: {result.context.text}"
            for result in results
        )
        language_instruction = "Write in Polish." if language == "pl" else "Write in English."
        user_prompt = (
            f"{language_instruction}\nSituation:\n{situation}\n\nSupplied passages:\n{passages}"
        )
        payload = {
            "model": self.settings.hf_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
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
        summary = str(data["summary"]).strip()
        actions = [str(action).strip() for action in data["suggested_actions"]][:3]
        valid_ids = {
            Retriever.source_id(result.passage)
            for result in results
        }
        selected_sources = data.get("selected_sources", [])
        source_ids: tuple[str, ...] = ()
        explanations: dict[str, str] = {}
        if isinstance(selected_sources, list):
            pairs = []
            for item in selected_sources[:3]:
                if not isinstance(item, dict):
                    continue
                source_id = self._canonical_source_id(str(item.get("id", "")), valid_ids)
                parts = [
                    str(item.get(field, "")).strip()
                    for field in (
                        "speaker_and_audience",
                        "immediate_context",
                        "original_meaning",
                        "situation_application",
                    )
                ]
                explanation = " ".join(part for part in parts if part)
                # Accept the earlier single-field shape from providers that
                # continue to imitate it despite the updated schema.
                if not explanation:
                    explanation = str(item.get("explanation", "")).strip()
                pairs.append((source_id, explanation))
            source_ids = tuple(source_id for source_id, explanation in pairs if source_id in valid_ids and explanation)
            explanations = {
                source_id: explanation
                for source_id, explanation in pairs
                if source_id in valid_ids and explanation
            }
        # Accept the previous shape during rolling deployments and from models
        # that imitate an earlier response found in their context.
        if not source_ids:
            source_ids = tuple(
                self._canonical_source_id(str(source_id), valid_ids)
                for source_id in data.get("selected_source_ids", [])[:3]
                if self._canonical_source_id(str(source_id), valid_ids)
            )
            raw_explanations = data.get("source_explanations", {})
            if isinstance(raw_explanations, dict):
                explanations = {
                    source_id: str(raw_explanations.get(source_id, "")).strip()
                    for source_id in source_ids
                    if str(raw_explanations.get(source_id, "")).strip()
                }
        if not summary or not actions or not source_ids or len(explanations) != len(source_ids):
            raise ValueError("Empty model response")
        return GeneratedReflection(
            summary,
            actions,
            f"hugging-face:{self.settings.hf_model}",
            source_ids,
            explanations,
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
            explanations = {
                Retriever.source_id(result.passage): relevance_note(result.themes, language)
                for result in selected_results
            }
            return GeneratedReflection(
                summary, actions[:3], "local-extractive", tuple(explanations), explanations
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
        explanations = {
            Retriever.source_id(result.passage): relevance_note(result.themes, language)
            for result in selected_results
        }
        return GeneratedReflection(
            summary, actions[:3], "local-extractive", tuple(explanations), explanations
        )
