#!/usr/bin/env python3
"""Run paired application prompts on the eight adjudicated sources, without retrieval."""

import argparse
import asyncio
import hashlib
import json
import random
from pathlib import Path
from time import perf_counter

import httpx

from app.application_experiment import PromptVariant, parse_application, prompt_for
from app.blind_review import canonical_reference
from app.config import get_settings


ROOT = Path(__file__).parents[1]


async def run(output: Path) -> None:
    if output.exists():
        raise ValueError("Output directory exists")
    settings = get_settings()
    if not settings.hf_token:
        raise ValueError("Configured inference token is required")
    source_path = ROOT / "evaluation/calibration-v1/adjudication.json"
    items = json.loads(source_path.read_text())["items"]
    baseline = json.loads((ROOT / "evaluation/runs/baseline.json").read_text())["results"]
    reranker = json.loads((ROOT / "evaluation/runs/reranker.json").read_text())["results"]
    sources = {}
    for row in baseline + reranker:
        for source in row["response"]["sources"]:
            sources.setdefault((row["id"], canonical_reference(source["reference"])), source)
    tasks = [(item, variant, repeat) for item in items for variant in PromptVariant
             for repeat in (1, 2)]
    random.Random(20260913).shuffle(tasks)
    output.mkdir(parents=True)
    records = []
    async with httpx.AsyncClient(timeout=settings.hf_timeout_seconds) as client:
        for item, variant, repeat in tasks:
            source = sources[item["id"][:6], canonical_reference(item["reference"])]
            source_id = item["id"]
            user_prompt = (
                f"Write in Polish. Generate an application for exactly the supplied source, retaining "
                f"its ID. Do not choose a different passage.\nSituation:\n{item['situation']}\n\n"
                f"[ID {source_id}] Selected verse: {item['reference']}: {item['quotation']}\n"
                f"Reviewed context: {source.get('origin_context', '')} "
                f"{source.get('broader_context', '')}\n"
                f"Reviewed original meaning: {source.get('original_meaning', '')}"
            )
            payload = {"model": settings.hf_model_pl, "temperature": 0.15,
                       "max_tokens": settings.hf_max_tokens,
                       "response_format": {"type": "json_object"},
                       "messages": [{"role": "system", "content": prompt_for(variant)},
                                    {"role": "user", "content": user_prompt}]}
            record = {"id": source_id, "variant": variant, "repeat": repeat,
                      "payload": payload}
            started = perf_counter()
            try:
                response = await client.post(
                    f"{settings.hf_base_url.rstrip('/')}/chat/completions",
                    headers={"Authorization": f"Bearer {settings.hf_token}"}, json=payload)
                response.raise_for_status()
                raw = response.json()["choices"][0]["message"]["content"]
                record["raw_content"] = raw
                record["application"] = parse_application(json.loads(raw), source_id)
            except (httpx.HTTPError, ValueError, KeyError, TypeError, IndexError) as error:
                record["error_type"] = type(error).__name__
            record["seconds"] = perf_counter() - started
            records.append(record)
            with (output / "responses.jsonl").open("a") as log:
                log.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"Completed {len(records)}/{len(tasks)}; errors: "
                  f"{sum('error_type' in value for value in records)}", flush=True)
    result = {"kind": "fixed-source-prompt-experiment", "records": records,
              "input_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "limitations": "Eight selected development cases, two repeats. No retrieval, retries, "
                              "or fallback. Control uses the production system prompt but forces "
                              "one source; this is not a full production request."}
    (output / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(run(args.output))


if __name__ == "__main__":
    main()
