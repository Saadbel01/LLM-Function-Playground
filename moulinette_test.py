from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_moulinette_exercises(repo_root: Path) -> dict:
    """Load exercises from moulinette/moulinette/functions_definition.py."""
    moulinette_src = repo_root / "moulinette"
    if str(moulinette_src) not in sys.path:
        sys.path.insert(0, str(moulinette_src))

    from moulinette.functions_definition import exercises  # type: ignore

    return exercises


def build_corrections(exercises: dict) -> list[dict[str, Any]]:
    """Reproduce moulinette corrections generation."""
    corrections: list[dict[str, Any]] = []
    for fn_to_call, exercise_list in exercises.items():
        for exercise in exercise_list:
            fn_args = exercise["fn_args"]
            corrections.append(
                {
                    "prompt": exercise["prompt"],
                    "fn_name": fn_to_call.__name__,
                    "fn_args": fn_args,
                    "expected_output": fn_to_call(**fn_args),
                }
            )
    return corrections


def normalize_student_answer(item: dict[str, Any]) -> dict[str, Any]:
    """Accept both current project output and moulinette output keys."""
    fn_name = item.get("fn_name", item.get("name"))
    fn_args = item.get("args", item.get("parameters"))
    return {
        "prompt": item.get("prompt"),
        "fn_name": fn_name,
        "fn_args": fn_args,
    }


def evaluate(
    student_answers: list[dict[str, Any]],
    corrections: list[dict[str, Any]],
    exercises: dict,
) -> int:
    fn_name_to_function = {fn.__name__: fn for fn in exercises.keys()}
    correction_by_prompt = {
        correction["prompt"]: correction for correction in corrections
    }

    total_score = 0
    checked = 0
    skipped = 0

    for raw_student_answer in student_answers:
        print("-" * 100)
        student_answer = normalize_student_answer(raw_student_answer)
        print(f"Student answer: {student_answer}")

        prompt = student_answer.get("prompt")
        if not isinstance(prompt, str):
            print("INVALID EXERCISE: invalid or missing prompt in JSON")
            continue

        correction = correction_by_prompt.get(prompt)
        if correction is None:
            skipped += 1
            print("SKIPPED: prompt not present in moulinette exercises")
            continue

        checked += 1
        print(f"Correction: {correction}")

        fn_name = student_answer.get("fn_name")
        fn_args = student_answer.get("fn_args")

        if not isinstance(fn_name, str):
            print("INVALID EXERCISE: wrong function name")
            continue

        if not isinstance(fn_args, dict):
            print("INVALID EXERCISE: wrong function arguments")
            continue

        try:
            fn = fn_name_to_function[fn_name]
        except Exception as e:
            print(f"Error: {e}")
            print("INVALID EXERCISE: wrong function name")
            continue

        try:
            student_output = fn(**fn_args)
        except Exception as e:
            print(f"Error: {e}")
            print("INVALID EXERCISE: wrong function arguments")
            continue

        if student_output != correction["expected_output"]:
            print(
                "Output mismatch:"
                f" {student_output} != {correction['expected_output']}"
            )
            print("INVALID EXERCISE: wrong output")
            continue

        total_score += 1
        print("VALID EXERCISE")

    print("-" * 100)
    print(f"Checked (matched prompts): {checked}")
    print(f"Skipped (not in moulinette): {skipped}")
    print(f"Total score: {total_score}/{checked}")

    return total_score


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate function-calling outputs with the same logic "
            "as moulinette."
        )
    )
    parser.add_argument(
        "--student-answer-path",
        default="data/output/function_calling_results.json",
        help="Path to your generated function-calling results JSON.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    student_path = (repo_root / args.student_answer_path).resolve()

    if not student_path.exists():
        raise FileNotFoundError(
            f"Student answer file not found: {student_path}"
        )

    with open(student_path, "r", encoding="utf-8") as f:
        student_answers = json.load(f)

    if not isinstance(student_answers, list):
        raise ValueError("Student answer JSON must be a list of objects.")

    exercises = load_moulinette_exercises(repo_root)
    corrections = build_corrections(exercises)
    evaluate(student_answers, corrections, exercises)


if __name__ == "__main__":
    main()
