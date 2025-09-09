# Contributing to assistant_core

Thank you for your interest in contributing to `assistant_core`! This document explains how to set up a local development environment, run tests and linters, and submit changes so maintainers can review them quickly.

## Quick start

1. Fork the repository and create a topic branch from `main`:

   - Branch name example: `fix/resolver-node-bug` or `feat/add-promptnode-test`

2. Install dependencies (Poetry is used for dependency management):

```bash
poetry install
```

3. Copy environment variables from the example and set any secrets locally:

```bash
cp .env.example .env
# then set OPENAI_API_KEY in .env or export it in your shell
export OPENAI_API_KEY="your_key_here"
```

Note: unit tests generally patch `OPENAI_API_KEY` where necessary. You don't need a real key to run the unit test suite, but integration tests (if added) may require a valid key.

## Run tests, formatters and linters

- Run tests:

```bash
make test
# or
poetry run pytest
```

- Format and sort imports:

```bash
make format
```

- Lint and check formatting (fast feedback before pushing):

```bash
make lint
```

CI runs the same formatting and lint checks on PRs. Fixing issues locally avoids CI noise.

## Coding guidelines

- Formatting: `black` is the canonical formatter. Use `isort` for import ordering. `make format` runs both.
- Linting: `flake8`. Keep new code clean and follow existing module patterns (module-level `_logger = logging.getLogger(__name__)`, small functions, clear docstrings).
- Typing: the project uses Python 3.12 typing. Add type hints where useful.
- Tests: add unit tests for bug fixes and new features. Prefer dependency injection or mocking when testing nodes that call external models.

## Commit & PR process

1. Make small, focused commits with clear messages.
2. Push your branch and open a PR against `main` with a short description of the change, motivation, and testing steps.
3. In your PR description, include a checklist like:
   - [ ] Tests added/updated
   - [ ] Linter/formatter run
   - [ ] Documentation updated (if applicable)

Maintainers will review, request changes if needed, and merge once CI passes and review is complete.

## Security and secrets

- Never commit secrets or credentials. Use `.env` (gitignored) or environment variables.
- If you discover a security issue, open a private issue and mark it security-related so maintainers can respond.

## Code of conduct

Be respectful and collaborative.

## Questions

If you're unsure where to start, open an issue with the label `help wanted` and a short description of what you'd like to do.

Thanks for contributing!
