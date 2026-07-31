import io
import json
import tarfile
from pathlib import Path

import httpx
import numpy as np
import pytest

from scripts.theme_discovery import (
    ETHICS_MEMBER,
    ClusterLabeler,
    PrincipleExtractor,
    PrincipleRecord,
    SourceScenario,
    cluster_principles,
    load_ethics_scenarios,
)


class DiscoveryEncoder:
    def encode(self, texts: str | list[str]) -> np.ndarray:
        assert isinstance(texts, list)
        return np.asarray(
            [[1.0, 0.0] if "truth" in text else [0.0, 1.0] for text in texts],
            dtype=np.float32,
        )


def test_load_ethics_scenarios_filters_long_records(tmp_path: Path) -> None:
    archive_path = tmp_path / "ethics.tar"
    content = (
        "label,input,is_short,edited\n"
        "0,I told the truth even though it was difficult.,True,False\n"
        "1,Too short.,True,False\n"
        "1,I hid the truth from a person who needed to know it.,False,False\n"
    ).encode()
    with tarfile.open(archive_path, "w") as archive:
        member = tarfile.TarInfo(ETHICS_MEMBER)
        member.size = len(content)
        archive.addfile(member, io.BytesIO(content))

    scenarios = load_ethics_scenarios(archive_path, max_records=10, random_seed=42)

    assert [scenario.text for scenario in scenarios] == [
        "I told the truth even though it was difficult."
    ]


def test_cluster_principles_uses_abstract_text_and_adds_review_fields() -> None:
    scenarios = [
        PrincipleRecord(
            SourceScenario(f"record-{index}", f"specific situation {index}"),
            f"truth principle {index}",
        )
        for index in range(4)
    ] + [
        PrincipleRecord(
            SourceScenario(f"record-{index}", f"another situation {index}"),
            f"care principle {index}",
        )
        for index in range(4, 8)
    ]

    rows, centroids = cluster_principles(
        scenarios,
        DiscoveryEncoder(),
        cluster_count=2,
        random_seed=42,
        examples_per_cluster=3,
    )

    assert len(rows) == 2
    assert all(row["license"] == "MIT" and row["reviewed"] is False for row in rows)
    assert all(len(row["examples"]) == 3 for row in rows)
    assert all(row["suggested_label_en"] is None for row in rows)
    assert all(row["suggested_label_pl"] is None for row in rows)
    assert all(row["summary_en"] is None and row["summary_pl"] is None for row in rows)
    assert all(row["suggested_existing_theme"] is None for row in rows)
    assert all(0.0 <= row["coherence"] <= 1.0 for row in rows)
    assert all("principle" in example for row in rows for example in row["examples"])
    assert np.allclose(np.linalg.norm(centroids, axis=1), 1.0)


@pytest.mark.asyncio
async def test_principle_extractor_batches_and_preserves_source_records() -> None:
    requests: list[dict] = []

    def respond(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        requests.append(payload)
        supplied = json.loads(payload["messages"][1]["content"])
        content = {
            "items": [
                {"record_id": item["record_id"], "principle": f"Principle for {item['record_id']}"}
                for item in supplied
            ]
        }
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(content)}}]},
        )

    scenarios = [SourceScenario(f"record-{index}", f"Situation {index}") for index in range(5)]
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        records = await PrincipleExtractor(
            client=client,
            base_url="https://example.test/v1",
            token="token",
            model="model",
            batch_size=2,
        ).extract(scenarios)

    assert len(requests) == 3
    assert [record.scenario for record in records] == scenarios
    assert records[0].principle == "Principle for record-0"


@pytest.mark.asyncio
async def test_principle_extractor_rejects_missing_batch_items() -> None:
    attempts = 0

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"items": []}'}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        extractor = PrincipleExtractor(client, "https://example.test/v1", "token", "model", 10)
        with pytest.raises(ValueError, match="complete principle batch"):
            await extractor.extract([SourceScenario("record-1", "Situation")])

    assert attempts == 3


@pytest.mark.asyncio
async def test_principle_extractor_retries_an_incomplete_batch() -> None:
    attempts = 0

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        content = {"items": []}
        if attempts == 2:
            content = {"items": [{"record_id": "record-1", "principle": "Respect for others"}]}
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(content)}}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        extractor = PrincipleExtractor(client, "https://example.test/v1", "token", "model", 10)
        records = await extractor.extract([SourceScenario("record-1", "Situation")])

    assert attempts == 2
    assert records[0].principle == "Respect for others"


@pytest.mark.asyncio
async def test_principle_extractor_splits_a_batch_that_stays_incomplete() -> None:
    batch_sizes: list[int] = []

    def respond(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        supplied = json.loads(payload["messages"][1]["content"])
        batch_sizes.append(len(supplied))
        items = [] if len(supplied) > 1 else [
            {"record_id": supplied[0]["record_id"], "principle": "General concern"}
        ]
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps({"items": items})}}]},
        )

    scenarios = [SourceScenario(f"record-{index}", "Situation") for index in range(2)]
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        extractor = PrincipleExtractor(client, "https://example.test/v1", "token", "model", 10)
        records = await extractor.extract(scenarios)

    assert batch_sizes == [2, 2, 2, 1, 1]
    assert [record.scenario for record in records] == scenarios


@pytest.mark.asyncio
async def test_cluster_labeler_adds_bilingual_editorial_metadata() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        content = {
            "items": [{
                "id": "cluster-1",
                "suggested_label_en": "Respect for Boundaries",
                "suggested_label_pl": "Szacunek dla Granic",
                "summary_en": "Respecting another person's limits.",
                "summary_pl": "Poszanowanie granic drugiej osoby.",
            }]
        }
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(content)}}]},
        )

    cluster = {
        "id": "cluster-1",
        "examples": [{"principle": "Respect for personal boundaries"}],
    }
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        rows = await ClusterLabeler(
            client, "https://example.test/v1", "token", "model"
        ).label([cluster])

    assert rows[0]["suggested_label_en"] == "Respect for Boundaries"
    assert rows[0]["suggested_label_pl"] == "Szacunek dla granic"
    assert rows[0]["summary_pl"] == "Poszanowanie granic drugiej osoby."
