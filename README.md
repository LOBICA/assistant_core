# Assistant Core

Lightweight core primitives and builders for assembling agent workflows with langchain and langgraph.

This package provides Node implementations, state types, builders, and a small factory pattern to compose
StateGraph-based agents used by the broader assistant projects.

[![CI](https://github.com/LOBICA/assistant_core/actions/workflows/main.yml/badge.svg)](https://github.com/LOBICA/assistant_core/actions)
[![Coverage](https://codecov.io/github/LOBICA/assistant_core/graph/badge.svg?token=7G3I1JQY6J)](https://codecov.io/github/LOBICA/assistant_core)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Quick start

Requirements: Python 3.12 and Poetry.

Clone and install (including dev dependencies):

```bash
git clone git@github.com:your-org/assistant_core.git
cd assistant_core
poetry install
```

Run tests:

```bash
make test
# or
poetry run pytest
```

Install and run pre-commit hooks (pre-commit hooks call the Poetry-installed tools):

```bash
make pre-commit
```

## Development & contributing

See `CONTRIBUTING.md` for full contributor guidance. Common developer commands:

- Install dependencies: `make install`
- Format code: `make format`
- Lint checks: `make lint`
- Run tests: `make test`
- Install and run pre-commit hooks: `make pre-commit`

Notes
- Pre-commit hooks in this repo are configured to call the Poetry-installed tools (black, isort, flake8). Make sure to run `make install` before `make pre-commit`.

## Architecture and build references

- `ARCHITECTURE.md` — package architecture focused on builders, nodes, and state flow.
- `AGENT_BUILD_REFERENCE.md` — step-by-step instructions to build an agent from scratch with assistant_core.

## Project layout

- `assistant_core/` — main package
	- `nodes/` — Node implementations and mixins
	- `builder/` — Directors/builders and build context
	- `factories.py` — ContextFactory and component factory extension points
	- `models.py` — model adapter loader
	- `state.py` — typed state classes used by nodes

Extension points
- Use `ContextFactory`/`BuilderContext.create(...)` to provide model, graph, resolver, and tools factories.
- Add new Node types under `assistant_core/nodes/`.

## Troubleshooting

- If pre-commit or hooks report missing commands, run `make install` to ensure dev dependencies are available.

## License

This project is licensed under the MIT License — see `LICENSE` for details.

