.PHONY: install format lint typecheck test audit docs docs-serve quality

install:
	uv sync --group dev --group docs

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy src tests

test:
	uv run pytest

audit:
	uv run pip-audit

docs:
	uv run mkdocs build --strict

docs-serve:
	uv run mkdocs serve

quality:
	./scripts/check.sh
