from unittest.mock import AsyncMock, Mock

import pytest

from app.context import ContextCard
from app.generation import GeneratedReflection
from app.reflection_service import ReflectionService
from app.retrieval import Passage, SearchResult


@pytest.mark.asyncio
async def test_reflection_service_builds_response_from_collaborators():
    passage = Passage("Matthew", 5, 44, 44, "Love your enemies.")
    result = SearchResult(passage, passage, 1.0, 0.9, ("forgiveness",))
    retriever = Mock()
    retriever.search.return_value = [result]
    retriever.passage_range.return_value = passage
    generator = Mock()
    generator.generate = AsyncMock(
        return_value=GeneratedReflection(
            "Choose love.",
            ["Act patiently."],
            "local-extractive",
            ("Matthew:5:44-44",),
            {"Matthew:5:44-44": "Respond without retaliation."},
        )
    )
    context = ContextCard(
        id="matthew-5",
        book="Matthew",
        chapter_start=5,
        verse_start=43,
        chapter_end=5,
        verse_end=48,
        context_chapter=5,
        context_verse_start=43,
        context_verse_end=48,
        literary_type="Teaching",
        origin_context="Jesus teaches.",
        broader_context="The Sermon on the Mount.",
        original_meaning="Love extends to enemies.",
        context_sources=("Matthew 5",),
        confidence="high",
        reviewed=True,
    )
    contexts = Mock()
    contexts.for_passage.return_value = context

    response = await ReflectionService(retriever, generator, contexts).create(
        "A sufficiently detailed situation needing a loving response.",
        "en",
    )

    assert response.summary == "Choose love."
    assert response.sources[0].reference == "Matthew 5:44"
    assert response.sources[0].situation_application == "Respond without retaliation."
    generator.generate.assert_awaited_once()
