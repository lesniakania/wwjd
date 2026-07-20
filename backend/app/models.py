from pydantic import BaseModel, Field, field_validator

from .config import get_settings
from .localization import Language


class ReflectionRequest(BaseModel):
    situation: str = Field(min_length=20)
    language: Language = "pl"

    @field_validator("situation")
    @classmethod
    def clean_situation(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) > get_settings().max_situation_length:
            raise ValueError("Situation is too long")
        return cleaned


class Source(BaseModel):
    reference: str
    quotation: str
    translation: str = "World English Bible (WEB)"
    context_note: str | None = None
    relevance: str
    context_reference: str
    context_quotation: str


class ReflectionResponse(BaseModel):
    summary: str
    suggested_actions: list[str] = Field(min_length=1, max_length=3)
    sources: list[Source] = Field(min_length=1, max_length=5)
    safety_message: str | None = None
    limitations: str
    generated_with: str


class HealthResponse(BaseModel):
    status: str
    verses: int
    generation_mode: str
