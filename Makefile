export PATH := $(HOME)/.local/bin:$(PATH)
install:
	pip install uv
	uv sync

run:
	uv run python -m src --functions_definition input/functions_definition.json --input input/function_calling_tests.json --output data/output/function_calling_results.json

test:
	uv run python3 test_result.py

debug:
	uv run python3 -m pdb src

clean:
	rm -rf **/__pycache__  .mypy_cache __pycache__

lint:
	uv run flake8 . --exclude=.venv,moulinette,llm_sdk
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
lint-strict:
	uv run flake8 .
	uv run mypy . --strict

.PHONY: install run debug clean lint lint-strict