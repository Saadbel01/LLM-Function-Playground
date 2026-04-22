
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

test:
	uv run python3 -m src --functions_definition moulinette/moulinette/successfully/input/functions_definition.json --input moulinette/moulinette/successfully/input/function_calling_tests.json 

grede:
	uv run python3 -m moulinette grade_student_answers /home/sbelcadi/goinfre/LLM-Function-Playground/data/output/function_calling_results.json --set private --student successfully

.PHONY: install run debug clean lint lint-strict