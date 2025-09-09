# Assistant Core

Lightweight core primitives and builders for assembling agent workflows with langchain and langgraph.

This package provides Node implementations, state types, builders, and a small factory pattern to compose
StateGraph-based agents used by the broader assistant projects.

<!-- Badges: add CI/coverage badges when available -->

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

## Project layout

- `assistant_core/` — main package
	- `nodes/` — Node implementations and mixins
	- `builder.py` — Director/Builder for StateGraph composition
	- `factories.py` — BaseAgentFactory (extension point)
	- `models.py` — model adapter loader
	- `state.py` — typed state classes used by nodes

Extension points
- Implement a subclass of `BaseAgentFactory` to provide a model and tools.
- Add new Node types under `assistant_core/nodes/`.

## Troubleshooting

- If pre-commit or hooks report missing commands, run `make install` to ensure dev dependencies are available.

## License

This project is licensed under the MIT License — see `LICENSE` for details.

