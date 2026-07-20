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


@dataclass(frozen=True)
class GeneratedAnswer:
    answer: str
    mode: str
    source_ids: tuple[str, ...] = ()


class ChatModelUnavailable(RuntimeError):
    """Raised when a genuine generative conversation cannot be provided."""


SYSTEM_PROMPT = """You write a cautious, compassionate Bible-grounded reflection.
Use only the supplied passages as scriptural evidence. Do not add Bible references or quotations.
Never claim certainty about what Jesus would do. Distinguish an application from the passage itself.
Do not advise secrecy, retaliation, or remaining in danger. Professional and emergency help take priority.
Explain the connection between the situation and the supplied passages; do not merely summarize them.
Return strict JSON with keys summary (2-4 sentences) and suggested_actions (1-3 short strings)."""

CHAT_SYSTEM_PROMPT = """You continue a conversation that helps a user understand Bible passages.
Use only the supplied passages as scriptural evidence. Never invent a quotation or Bible reference.
Directly answer the latest question in 2-5 concise paragraphs. Explain separately what the passage
says in context and how it may apply; explicitly say when an application goes beyond the text.
Correct readings that blame an entire group for one person's actions or use a descriptive hostile-nation
passage as a command about modern ethnic groups. Do not claim certainty about what Jesus would do.
Do not advise secrecy, retaliation, or remaining in danger. The passages under CURRENTLY DISCUSSED
are the referent of phrases such as "this passage". CANDIDATE PASSAGES are alternatives retrieved for
the original situation. Never discuss a Bible reference absent from both supplied groups, even if it
appeared in earlier conversation. Return JSON with keys answer and source_ids (the IDs actually used)."""


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

    async def answer_followup(
        self,
        situation: str,
        question: str,
        history: list[dict[str, str]],
        results: list[SearchResult],
        current_results: list[SearchResult],
        language: Language,
    ) -> GeneratedAnswer:
        if not self.settings.hf_token:
            raise ChatModelUnavailable("HF_TOKEN is not configured")
        try:
            return await self._answer_followup_remote(
                situation, question, history, results, current_results, language
            )
        except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ChatModelUnavailable("The conversation model is unavailable") from error

    async def _answer_followup_remote(
        self,
        situation: str,
        question: str,
        history: list[dict[str, str]],
        results: list[SearchResult],
        current_results: list[SearchResult],
        language: Language,
    ) -> GeneratedAnswer:
        def format_passages(passages_to_format: list[SearchResult]) -> str:
            return "\n".join(
                f"[ID {result.passage.book}:{result.passage.chapter}:{result.passage.verse_start}-{result.passage.verse_end}] "
                f"Selected verse: {result.passage.reference}: {result.passage.text}\n"
                f"Context: {result.context.reference}: {result.context.text}"
                for result in passages_to_format
            ) or "(none)"
        current_passages = format_passages(current_results)
        candidate_passages = format_passages(results)
        language_instruction = "Write in Polish." if language == "pl" else "Write in English."
        messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
        messages.extend(history[-8:])
        messages.append(
            {
                "role": "user",
                "content": (
                    f"{language_instruction}\nOriginal situation:\n{situation}\n\n"
                    f"Latest question:\n{question}\n\nCURRENTLY DISCUSSED PASSAGES:\n{current_passages}\n\n"
                    f"CANDIDATE PASSAGES:\n{candidate_passages}"
                ),
            }
        )
        payload = {
            "model": self.settings.hf_model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 650,
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
        content = str(response.json()["choices"][0]["message"]["content"]).strip()
        data = self._parse_chat_content(content)
        answer = data["answer"]
        if not answer:
            raise ValueError("Empty model response")
        return GeneratedAnswer(
            answer,
            f"hugging-face:{self.settings.hf_model}",
            tuple(data["source_ids"]),
        )

    @staticmethod
    def _parse_chat_content(content: str) -> dict[str, object]:
        """Accept strict JSON, fenced JSON, or useful plain prose from chat providers."""
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.removeprefix("```json").removeprefix("```")
            stripped = stripped.removesuffix("```").strip()
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            start, end = stripped.find("{"), stripped.rfind("}")
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(stripped[start : end + 1])
                except json.JSONDecodeError:
                    parsed = {"answer": content, "source_ids": []}
            else:
                parsed = {"answer": content, "source_ids": []}
        if not isinstance(parsed, dict):
            return {"answer": content, "source_ids": []}
        answer = str(parsed.get("answer", "")).strip()
        source_ids = parsed.get("source_ids", [])
        if not isinstance(source_ids, list):
            source_ids = []
        return {
            "answer": answer or content,
            "source_ids": [str(source_id) for source_id in source_ids[:4]],
        }

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
