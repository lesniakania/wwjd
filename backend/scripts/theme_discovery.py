#!/usr/bin/env python3
"""Build an editorial theme queue from abstract principles in licensed ETHICS data."""

import argparse
import asyncio
import csv
import io
import json
import random
import tarfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx
import numpy as np
from sklearn.cluster import MiniBatchKMeans

from app.config import get_settings
from app.retrieval import SemanticEncoder


ETHICS_MEMBER = "ethics/commonsense/cm_train.csv"
ETHICS_PROJECT_URL = "https://github.com/hendrycks/ethics"

PRINCIPLE_SYSTEM_PROMPT = """You extract the general ethical concern behind situations.
Return JSON only: {"items":[{"record_id":"...","principle":"..."}]}.
For every input return exactly one concise English noun phrase (3-12 words). Abstract away people,
places, objects, protected traits and story details. Describe the ethical concern neutrally, not a
verdict and not an action from the story. Prefer concepts such as honesty under pressure, respect
for boundaries, proportional response, care for vulnerable people, or responsible stewardship."""

LABEL_SYSTEM_PROMPT = """You name candidate ethical themes for editorial review.
Return JSON only: {"items":[{"id":"...","suggested_label_en":"...",
"suggested_label_pl":"...","summary_en":"...","summary_pl":"..."}]}.
Return exactly one item per cluster. Labels must be broad noun phrases, natural in each language,
and reusable across different situations. Summaries must be one neutral sentence. Do not mention
dataset examples, people, places, or objects."""


@dataclass(frozen=True)
class SourceScenario:
    record_id: str
    text: str


@dataclass(frozen=True)
class PrincipleRecord:
    scenario: SourceScenario
    principle: str


def parse_json_content(response: httpx.Response) -> Any:
    response.raise_for_status()
    raw = str(response.json()["choices"][0]["message"]["content"]).strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


class PrincipleExtractor:
    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        token: str,
        model: str,
        batch_size: int,
    ) -> None:
        self.client = client
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.token = token
        self.model = model
        self.batch_size = batch_size

    async def extract(self, scenarios: list[SourceScenario]) -> list[PrincipleRecord]:
        records: list[PrincipleRecord] = []
        for offset in range(0, len(scenarios), self.batch_size):
            batch = scenarios[offset : offset + self.batch_size]
            records.extend(await self._extract_batch(batch))
        return records

    async def _extract_batch(self, batch: list[SourceScenario]) -> list[PrincipleRecord]:
        supplied = [asdict(scenario) for scenario in batch]
        expected_ids = {scenario.record_id for scenario in batch}
        for _attempt in range(3):
            response = await self.client.post(
                self.url,
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": PRINCIPLE_SYSTEM_PROMPT},
                        {"role": "user", "content": json.dumps(supplied)},
                    ],
                    "temperature": 0.1,
                    "max_tokens": max(1000, len(batch) * 30),
                    "response_format": {"type": "json_object"},
                },
            )
            parsed = parse_json_content(response)
            items = parsed.get("items", []) if isinstance(parsed, dict) else []
            by_id = {
                str(item.get("record_id")): str(item.get("principle", "")).strip()
                for item in items
                if isinstance(item, dict)
            }
            if set(by_id) == expected_ids and all(by_id.values()):
                return [PrincipleRecord(scenario, by_id[scenario.record_id]) for scenario in batch]
        if len(batch) == 1:
            raise ValueError("Model did not return a complete principle batch after 3 attempts")
        midpoint = len(batch) // 2
        return [
            *await self._extract_batch(batch[:midpoint]),
            *await self._extract_batch(batch[midpoint:]),
        ]


class ClusterLabeler:
    def __init__(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        token: str,
        model: str,
        batch_size: int = 10,
    ) -> None:
        self.client = client
        self.url = f"{base_url.rstrip('/')}/chat/completions"
        self.token = token
        self.model = model
        self.batch_size = batch_size

    async def label(self, clusters: list[dict]) -> list[dict]:
        result: list[dict] = []
        required = {"suggested_label_en", "suggested_label_pl", "summary_en", "summary_pl"}
        for offset in range(0, len(clusters), self.batch_size):
            batch = clusters[offset : offset + self.batch_size]
            supplied = [
                {
                    "id": cluster["id"],
                    "principles": [example["principle"] for example in cluster["examples"]],
                }
                for cluster in batch
            ]
            response = await self.client.post(
                self.url,
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": LABEL_SYSTEM_PROMPT},
                        {"role": "user", "content": json.dumps(supplied)},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 3000,
                    "response_format": {"type": "json_object"},
                },
            )
            parsed = parse_json_content(response)
            items = parsed.get("items", []) if isinstance(parsed, dict) else []
            by_id = {str(item.get("id")): item for item in items if isinstance(item, dict)}
            if set(by_id) != {cluster["id"] for cluster in batch} or any(
                not required <= set(by_id[cluster["id"]]) for cluster in batch
            ):
                raise ValueError("Model did not return a complete cluster label batch")
            for cluster in batch:
                labels = by_id[cluster["id"]]
                generated_fields = {field: str(labels[field]).strip() for field in required}
                polish_label = generated_fields["suggested_label_pl"]
                generated_fields["suggested_label_pl"] = (
                    polish_label[:1].upper() + polish_label[1:].lower()
                )
                result.append(
                    {
                        **cluster,
                        **generated_fields,
                    }
                )
        return result


def load_ethics_scenarios(
    archive_path: Path,
    max_records: int,
    random_seed: int,
) -> list[SourceScenario]:
    with tarfile.open(archive_path) as archive:
        member = archive.getmember(ETHICS_MEMBER)
        extracted = archive.extractfile(member)
        if extracted is None:
            raise ValueError(f"Missing {ETHICS_MEMBER} in {archive_path}")
        reader = csv.DictReader(io.TextIOWrapper(extracted, encoding="utf-8"))
        scenarios = [
            SourceScenario(f"ethics:commonsense:train:{index}", row["input"].strip())
            for index, row in enumerate(reader, start=2)
            if row["is_short"] == "True" and 30 <= len(row["input"].strip()) <= 500
        ]
    randomizer = random.Random(random_seed)
    randomizer.shuffle(scenarios)
    return scenarios[:max_records]


def cluster_principles(
    records: list[PrincipleRecord],
    encoder: SemanticEncoder,
    cluster_count: int,
    random_seed: int,
    examples_per_cluster: int,
) -> tuple[list[dict], np.ndarray]:
    embeddings = encoder.encode([record.principle for record in records])
    model = MiniBatchKMeans(
        n_clusters=cluster_count,
        random_state=random_seed,
        batch_size=512,
        n_init="auto",
    )
    labels = model.fit_predict(embeddings)
    centroids = model.cluster_centers_.astype(np.float32)
    centroids /= np.maximum(np.linalg.norm(centroids, axis=1, keepdims=True), 1e-12)

    rows: list[dict] = []
    retained_centroids: list[np.ndarray] = []
    for cluster_index in range(cluster_count):
        member_indexes = np.flatnonzero(labels == cluster_index)
        if len(member_indexes) < examples_per_cluster:
            continue
        similarities = embeddings[member_indexes] @ centroids[cluster_index]
        representative_indexes = member_indexes[np.argsort(similarities)[::-1][:examples_per_cluster]]
        rows.append(
            {
                "id": f"ethics-principle-cluster-{cluster_index + 1:03d}",
                "source": "ETHICS commonsense",
                "source_url": ETHICS_PROJECT_URL,
                "license": "MIT",
                "cluster_size": int(len(member_indexes)),
                "coherence": round(float(np.clip(np.mean(similarities), 0.0, 1.0)), 4),
                "theme": None,
                "suggested_existing_theme": None,
                "suggested_label_en": None,
                "suggested_label_pl": None,
                "summary_en": None,
                "summary_pl": None,
                "status": "draft",
                "reviewed": False,
                "examples": [
                    {
                        "record_id": records[index].scenario.record_id,
                        "text": records[index].scenario.text,
                        "principle": records[index].principle,
                    }
                    for index in representative_indexes
                ],
            }
        )
        retained_centroids.append(centroids[cluster_index])
    return rows, np.stack(retained_centroids)


def read_principle_cache(path: Path) -> list[PrincipleRecord] | None:
    if not path.exists():
        return None
    rows = json.loads(path.read_text(encoding="utf-8"))
    return [PrincipleRecord(SourceScenario(row["record_id"], row["text"]), row["principle"]) for row in rows]


def write_principle_cache(path: Path, records: list[PrincipleRecord]) -> None:
    rows = [
        {"record_id": record.scenario.record_id, "text": record.scenario.text,
         "principle": record.principle}
        for record in records
    ]
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


async def run(args: argparse.Namespace) -> None:
    settings = get_settings()
    if not settings.hf_token:
        raise ValueError("HF_TOKEN is required to abstract and label ethical principles")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cache_path = args.output_dir / "theme_principle_cache.json"
    records = read_principle_cache(cache_path) or []
    async with httpx.AsyncClient(timeout=settings.hf_timeout_seconds) as client:
        scenarios = load_ethics_scenarios(args.archive, args.max_records, args.seed)
        completed_ids = {record.scenario.record_id for record in records}
        pending = [scenario for scenario in scenarios if scenario.record_id not in completed_ids]
        extractor = PrincipleExtractor(
            client, settings.hf_base_url, settings.hf_token, settings.hf_model, args.batch_size
        )
        checkpoint_size = args.batch_size * 10
        for offset in range(0, len(pending), checkpoint_size):
            checkpoint = pending[offset : offset + checkpoint_size]
            batches = [
                checkpoint[index : index + args.batch_size]
                for index in range(0, len(checkpoint), args.batch_size)
            ]
            extracted_batches = await asyncio.gather(
                *(extractor.extract(batch) for batch in batches)
            )
            records.extend(record for batch in extracted_batches for record in batch)
            write_principle_cache(cache_path, records)
        rows, centroids = cluster_principles(
            records, SemanticEncoder(args.model), args.clusters, args.seed, args.examples
        )
        rows = await ClusterLabeler(
            client, settings.hf_base_url, settings.hf_token, settings.hf_model_pl
        ).label(rows)
    (args.output_dir / "theme_cluster_drafts.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    np.save(args.output_dir / "theme_cluster_centroids.npy", centroids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parents[1] / "app" / "data")
    parser.add_argument("--model", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    parser.add_argument("--clusters", type=int, default=90)
    parser.add_argument("--max-records", type=int, default=6000)
    parser.add_argument("--examples", type=int, default=6)
    parser.add_argument("--batch-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
