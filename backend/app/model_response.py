import json
import re
from dataclasses import dataclass
from typing import Any

from .localization import Language


@dataclass(frozen=True)
class ParsedModelResponse:
    summary: str
    actions: list[str]
    source_ids: tuple[str, ...]
    applications: dict[str, str]


class ModelResponseParser:
    """Validate and normalize the model provider's response."""

    def __init__(self, valid_source_ids: set[str]) -> None:
        self.valid_source_ids = valid_source_ids

    def parse(self, content: str, language: Language) -> ParsedModelResponse:
        data = self._parse_json(content)
        summary = self.plain_text(data["summary"])
        actions = [self.plain_text(action) for action in data["suggested_actions"]][:3]
        source_ids, applications = self._sources(data, language)
        if not summary or not actions or not source_ids or len(applications) != len(source_ids):
            raise ValueError("Empty model response")
        return ParsedModelResponse(summary, actions, source_ids, applications)

    def _sources(
        self, data: dict[str, Any], language: Language
    ) -> tuple[tuple[str, ...], dict[str, str]]:
        selected_sources = data.get("selected_sources", [])
        pairs: list[tuple[str, str]] = []
        if isinstance(selected_sources, list):
            for item in selected_sources[:3]:
                if not isinstance(item, dict):
                    continue
                source_id = self.canonical_source_id(str(item.get("id", "")))
                application = self.plain_text(item.get("situation_application", ""))
                if language == "pl" and self.has_unnatural_polish(application):
                    raise ValueError("Unnatural Polish application")
                if source_id in self.valid_source_ids and application:
                    pairs.append((source_id, application))
        if pairs:
            return tuple(source_id for source_id, _ in pairs), dict(pairs)
        return self._legacy_sources(data)

    def _legacy_sources(
        self, data: dict[str, Any]
    ) -> tuple[tuple[str, ...], dict[str, str]]:
        source_ids = tuple(
            canonical
            for source_id in data.get("selected_source_ids", [])[:3]
            if (canonical := self.canonical_source_id(str(source_id)))
        )
        raw_applications = data.get("source_explanations", {})
        if not isinstance(raw_applications, dict):
            return source_ids, {}
        applications = {
            source_id: str(raw_applications.get(source_id, "")).strip()
            for source_id in source_ids
            if str(raw_applications.get(source_id, "")).strip()
        }
        return source_ids, applications

    def canonical_source_id(self, source_id: str) -> str:
        if source_id in self.valid_source_ids:
            return source_id
        for valid_id in self.valid_source_ids:
            _, separator, final_range = valid_id.rpartition(":")
            start, _, end = final_range.partition("-")
            if separator and start == end and source_id == valid_id.removesuffix(f"-{end}"):
                return valid_id
        return ""

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
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
    def plain_text(value: object) -> str:
        if isinstance(value, (list, tuple)):
            return " ".join(
                part for item in value if (part := ModelResponseParser.plain_text(item))
            )
        text = str(value).strip()
        text = re.sub(
            r"\*\*(.+?)\*\*|__(.+?)__",
            lambda match: match.group(1) or match.group(2),
            text,
        )
        return text.replace("`", "").strip()

    @staticmethod
    def has_unnatural_polish(text: str) -> bool:
        rejected = (
            "aplikacja ma ograniczenia",
            "powinien się wchodzić",
            "powinna się wchodzić",
            "powinni się wchodzić",
            "nieprzywilejowania się",
            "nieprzywilejować się",
        )
        return any(phrase in text.lower() for phrase in rejected)
