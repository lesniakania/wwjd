import argparse
import json
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from types import SimpleNamespace
from pathlib import Path

import pytest
from fastapi import FastAPI

import scripts.evaluate as evaluate_script

from scripts.evaluate import run, save_report


DATASET = Path(__file__).parents[1] / "evaluation" / "cases.pl.json"


def test_saved_reports_cannot_be_overwritten(tmp_path: Path) -> None:
    path = tmp_path / "report.json"
    save_report(path, {"original": True})
    with pytest.raises(FileExistsError):
        save_report(path, {"original": False})
    assert json.loads(path.read_text()) == {"original": True}


async def test_rescore_cli_makes_no_network_call(tmp_path: Path) -> None:
    case = json.loads(DATASET.read_text())[0]
    original = tmp_path / "original.json"
    original.write_text(json.dumps({"dataset_sha256": "old", "results": [{
        "id": case["id"], "situation": case["situation"],
        "response": {"sources": [{"reference": case["expected_sources"][0]["reference"]}]},
    }]}))
    args = argparse.Namespace(
        dataset=DATASET, reviewed_only=True, limit=1, repeat=1,
        output=tmp_path / "new.json", baseline=None, rescore=original, label="rescored",
        case_ids=None,
    )
    await run(args)
    assert json.loads(args.output.read_text())["summary"]["hit"] == 1


async def test_unknown_case_ids_fail_before_loading_models(tmp_path: Path) -> None:
    args = argparse.Namespace(
        dataset=DATASET, reviewed_only=True, limit=None, repeat=1,
        output=tmp_path / "new.json", baseline=None, rescore=None, label="test",
        case_ids="not-a-case",
    )
    with pytest.raises(ValueError, match="Unknown case IDs"):
        await run(args)


async def failing_endpoint() -> None:
    raise RuntimeError("Synthetic server failure")


@asynccontextmanager
async def empty_lifespan(application: FastAPI) -> AsyncIterator[None]:
    yield


async def test_local_client_records_server_errors_like_http_mode(monkeypatch) -> None:
    application = FastAPI()
    application.add_api_route("/failure", failing_endpoint)
    monkeypatch.setattr(evaluate_script, "app", application)
    monkeypatch.setattr(evaluate_script, "lifespan", empty_lifespan)
    monkeypatch.setattr(evaluate_script, "get_settings", lambda: SimpleNamespace())
    args = argparse.Namespace(local=True, diagnostics=True, timeout=1)
    async with evaluate_script.evaluation_client(args) as client:
        response = await client.get("/failure")
    assert response.status_code == 500
