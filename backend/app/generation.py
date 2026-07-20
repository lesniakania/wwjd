import json
from dataclasses import dataclass

import httpx

from .config import Settings
from .localization import Language, reference
from .retrieval import SearchResult


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


SYSTEM_PROMPT = """You write a cautious, compassionate Bible-grounded reflection.
Use only the supplied passages as scriptural evidence. Do not add Bible references or quotations.
Never claim certainty about what Jesus would do. Distinguish an application from the passage itself.
Do not advise secrecy, retaliation, or remaining in danger. Professional and emergency help take priority.
Explain the connection between the situation and the supplied passages; do not merely summarize them.
Return strict JSON with keys summary (2-4 sentences) and suggested_actions (1-3 short strings)."""


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
            try:
                return await self._generate_remote(situation, results, language)
            except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                pass
        return self._generate_local(results, language)

    async def _generate_remote(
        self, situation: str, results: list[SearchResult], language: Language
    ) -> GeneratedReflection:
        passages = "\n".join(
            f"[{index}] Selected verse: {result.passage.reference}: {result.passage.text}\n"
            f"Context: {result.context.reference}: {result.context.text}"
            for index, result in enumerate(results, start=1)
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
            "temperature": 0.2,
            "max_tokens": 500,
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
        content = response.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        summary = str(data["summary"]).strip()
        actions = [str(action).strip() for action in data["suggested_actions"]][:3]
        if not summary or not actions:
            raise ValueError("Empty model response")
        return GeneratedReflection(summary, actions, f"hugging-face:{self.settings.hf_model}")

    @staticmethod
    def _generate_local(results: list[SearchResult], language: Language) -> GeneratedReflection:
        primary = results[0].passage
        secondary = results[1].passage if len(results) > 1 else None
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
            return GeneratedReflection(summary, actions[:3], "local-extractive")
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
        return GeneratedReflection(summary, actions[:3], "local-extractive")
