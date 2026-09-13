import json
from types import SimpleNamespace

import httpx
from scripts import evaluate_applications

import pytest

from app.application_experiment import parse_application, prompt_for, PromptVariant
from app.generation import SYSTEM_PROMPT


def test_control_is_production_prompt_and_candidate_removes_mandatory_qualification() -> None:
    assert prompt_for(PromptVariant.CONTROL) == SYSTEM_PROMPT
    assert 'In the second, give a natural qualification' not in prompt_for(PromptVariant.GROUNDED)


def test_application_requires_exact_frozen_source() -> None:
    assert parse_application({'selected_sources': [{'id': 'source', 'situation_application': 'Text'}]}, 'source') == 'Text'
    with pytest.raises(ValueError):
        parse_application({'selected_sources': [{'id': 'other', 'situation_application': 'Text'}]}, 'source')


@pytest.mark.asyncio
async def test_experiment_records_provider_failures_without_fallback(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(evaluate_applications, 'get_settings', lambda: SimpleNamespace(
        hf_token='test', hf_timeout_seconds=1, hf_model_pl='test', hf_max_tokens=100,
        hf_base_url='https://test.invalid'))
    client = httpx.AsyncClient(transport=httpx.MockTransport(provider_failure))
    monkeypatch.setattr(evaluate_applications.httpx, 'AsyncClient', lambda **kwargs: client)
    await evaluate_applications.run(tmp_path / 'run')
    report = json.loads((tmp_path / 'run/report.json').read_text())
    assert len(report['records']) == 32
    assert all(row['error_type'] == 'HTTPStatusError' for row in report['records'])
    assert all('application' not in row for row in report['records'])
    assert 'provider-private-detail' not in json.dumps(report)


def provider_failure(request: httpx.Request) -> httpx.Response:
    return httpx.Response(503, text='provider-private-detail')
