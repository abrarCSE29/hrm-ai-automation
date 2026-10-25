.PHONY: setup migrate run test seed evals

setup:
	uv sync

migrate:
	uv run alembic upgrade head

run:
	uv run uvicorn app.main:app --reload --port 8000

test:
	uv run pytest

seed:
	uv run python scripts/seed.py

evals:
	uv run python scripts/run_evals.py
