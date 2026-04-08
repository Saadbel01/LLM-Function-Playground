
install:
	pip install uv
	uv sync

run:
	uv run -m src

test:
	uv run python3 test_result.py

debug:
	uv run python3 -m pdb src

clean:
	rm -rf **/__pycache__  .mypy_cache __pycache__

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

.PHONY: install run debug clean lint lint-strict