# Coding guidelines

This file is the single source of truth for maintainability expectations in this repository.
It applies to the FastAPI backend, the Vue frontend, scripts, and tests.

Keep the existing repository context in mind, including its FastAPI backend, Vue frontend,
established models, and file structure. These expectations apply to implementation and testing.
Add relevant tests for every change.

CLARIFY BEFORE ASSUMING — When something is unclear or multiple materially different solutions
are possible, ask for clarification, including during implementation. Do not repeatedly ask for
permission to run commands that have already been authorized.

TESTS FIRST — Before implementation work, write tests and verify that they fail for the expected
reason. This applies to features and bug fixes.

Deliver maintainable, production-quality code using the simplest solution that fits the existing
architecture. Follow the principles and checklist below.

## Important principles

- KISS
- YAGNI
- Separation of concerns
- DRY
- Single responsibility
- Open/closed principle

## Testing requirements

- Add focused unit tests for new classes and modules, following existing test patterns.
- Mock external API responses.

## Critical implementation checklist

- Follow the principles and testing requirements above.
- Use clear names; avoid one-letter names and unclear abbreviations.
- Do not define methods inside other methods unless necessary.
- Add docstrings only when they communicate useful information beyond a clear method name.
- Type all new Python and TypeScript methods and functions.
- Use enums instead of strings for closed sets of states where appropriate.
- Prefer guard clauses over unnecessary nested conditionals.
- Keep all imports at the top of each file; do not import inside methods.
- Avoid N+1 database queries; use eager loading where relevant.
- Write tests for new functionality.
- Run and fix all backend and frontend tests before completing a task.
- Run and fix all configured backend and frontend linting checks before completing a task.
