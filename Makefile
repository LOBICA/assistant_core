# Base Makefile for common dev tasks. Adjust POETRY and package names as needed.


POETRY ?= poetry
PYTEST_OPTS ?=
SRC_DIRS := assistant_core tests

.PHONY: help install lock update format lint test pre-commit release clean

help:
	@printf "Available targets:\n"
	@printf "  install        Install project dependencies (poetry install)\n"
	@printf "  lock           Update poetry.lock\n"
	@printf "  update         Update dependencies\n"
	@printf "  format         Run code formatters (black, isort)\n"
	@printf "  lint           Run linter (flake8)\n"
	@printf "  test           Run pytest\n"
	@printf "  pre-commit     Install and run pre-commit hooks\n"
	@printf "  release        Bump version, tag and push (usage: make release VERSION=patch)\n"
	@printf "  clean          Remove build/test caches\n"

install:
	$(POETRY) install

lock:
	$(POETRY) lock

update:
	$(POETRY) update

format:
	$(POETRY) run black $(SRC_DIRS)
	$(POETRY) run isort $(SRC_DIRS)

lint:
	$(POETRY) run black --check $(SRC_DIRS)
	$(POETRY) run isort --check $(SRC_DIRS)
	$(POETRY) run flake8 $(SRC_DIRS)
	@echo "Linting completed."

test:
	$(POETRY) run pytest $(PYTEST_OPTS)

pre-commit:
	$(POETRY) run pre-commit install
	$(POETRY) run pre-commit run --all-files

release:
	# Usage: make release VERSION=patch (or minor/major or explicit x.y.z)
	$(shell test -n "$(VERSION)" || echo "Missing VERSION. Usage: make release VERSION=patch" >&2)
	./scripts/new_version.sh $(VERSION)

clean:
	@find . -type d -name "__pycache__" -print0 | xargs -0 -r rm -rf
	@rm -rf .pytest_cache build dist htmlcov .mypy_cache .ruff_cache coverage.xml
