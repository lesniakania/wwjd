import json
from dataclasses import dataclass

import httpx

from .config import Settings
from .retrieval import SearchResult


LIMITATIONS = (
    "This is an AI-generated, Bible-grounded reflection—not a certain declaration of what Jesus "
    "would do, and not a substitute for pastoral, medical, legal, or mental-health advice."
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
Return strict JSON with keys summary (2-4 sentences) and suggested_actions (1-3 short strings)."""


class ReflectionGenerator:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def mode(self) -> str:
        return "hugging-face" if self.settings.hf_token else "local-extractive"

    async def generate(self, situation: str, results: list[SearchResult]) -> GeneratedReflection:
        if self.settings.hf_token:
            try:
                return await self._generate_remote(situation, results)
            except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError):
                pass
        return self._generate_local(results)

    async def _generate_remote(
        self, situation: str, results: list[SearchResult]
    ) -> GeneratedReflection:
        passages = "\n".join(
            f"[{index}] {result.passage.reference}: {result.passage.text}"
            for index, result in enumerate(results, start=1)
        )
        user_prompt = f"Situation:\n{situation}\n\nSupplied passages:\n{passages}"
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
    def _generate_local(results: list[SearchResult]) -> GeneratedReflection:
        primary = results[0].passage
        secondary = results[1].passage if len(results) > 1 else None
        summary = (
            f"A Bible-grounded approach begins with the principle expressed in {primary.reference}. "
            "Consider the situation honestly, with compassion for everyone affected, and choose an "
            "action consistent with the retrieved teaching rather than treating this as a certain answer."
        )
        actions = [
            f"Read {primary.reference} in its full chapter before deciding.",
            "Separate the known facts from assumptions, then choose the most truthful and loving next step.",
        ]
        if secondary:
            actions.append(f"Compare that application with the perspective in {secondary.reference}.")
        return GeneratedReflection(summary, actions[:3], "local-extractive")

