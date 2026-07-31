from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[2]


def test_ci_runs_all_repository_quality_checks() -> None:
    workflow = (REPOSITORY_ROOT / ".github/workflows/ci.yml").read_text()

    assert "uv run ruff check --output-format=github ." in workflow
    assert "uv run bandit -r app" in workflow
    assert "uv run pytest" in workflow
    assert "npm run lint" in workflow
    assert "npm run test" in workflow
    assert "npm run build" in workflow


def test_ci_scans_dependencies_and_repository_for_vulnerabilities() -> None:
    workflow = (REPOSITORY_ROOT / ".github/workflows/ci.yml").read_text()

    assert "aquasecurity/trivy-action" in workflow
    assert "scan-type: fs" in workflow
    assert "backend/uv.lock" in workflow
    assert "frontend/package-lock.json" in workflow


def test_frontend_exposes_non_mutating_lint_command() -> None:
    package_json = (REPOSITORY_ROOT / "frontend/package.json").read_text()

    assert '"lint": "eslint ."' in package_json
