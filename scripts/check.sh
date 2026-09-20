#!/usr/bin/env bash

set -euo pipefail

echo "==> Checking formatting"
uv run ruff format --check .

echo "==> Running lint checks"
uv run ruff check .

echo "==> Running static type checks"
uv run mypy src tests

echo "==> Running tests and coverage"
uv run pytest

echo "==> Auditing dependencies"
uv run pip-audit

echo "==> Building documentation"
uv run mkdocs build --strict

echo "==> GroceryPulse quality gate passed"
