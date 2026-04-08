import json
import math
import re
import sys
from pathlib import Path


def fn_add_numbers(a: float, b: float) -> float:
    assert isinstance(a, float)
    assert isinstance(b, float)
    return a + b


def fn_greet(name: str) -> str:
    assert isinstance(name, str)
    return f"Hello, {name}!"


def fn_multiply_numbers(a: float, b: float) -> float:
    assert isinstance(a, float)
    assert isinstance(b, float)
    return a * b


def fn_is_even(n: int) -> bool:
    assert isinstance(n, int)
    return n % 2 == 0


def fn_substitute_string_with_regex(
    source_string: str, regex: str, replacement: str
) -> str:
    assert isinstance(source_string, str)
    assert isinstance(regex, str)
    assert isinstance(replacement, str)
    return re.sub(regex, replacement, source_string)


def fn_get_square_root(a: float) -> float:
    assert isinstance(a, float)
    return math.sqrt(a)


def fn_reverse_string(s: str) -> str:
    assert isinstance(s, str)
    return s[::-1]


# exact exercises from moulinette
EXERCISES = [
    {
        "prompt": "What is the sum of 2 and 3?",
        "fn_name": "fn_add_numbers",
        "fn_args": {"a": 2.0, "b": 3.0},
    },
    {
        "prompt": "What is the sum of 265 and 345?",
        "fn_name": "fn_add_numbers",
        "fn_args": {"a": 265.0, "b": 345.0},
    },
    {
        "prompt": "Greet shrek",
        "fn_name": "fn_greet",
        "fn_args": {"name": "shrek"},
    },
    {
        "prompt": "Greet john",
        "fn_name": "fn_greet",
        "fn_args": {"name": "john"},
    },
    {
        "prompt": "Reverse the string 'hello'",
        "fn_name": "fn_reverse_string",
        "fn_args": {"s": "hello"},
    },
    {
        "prompt": "Reverse the string 'world'",
        "fn_name": "fn_reverse_string",
        "fn_args": {"s": "world"},
    },
    {
        "prompt": "What is the square root of 16?",
        "fn_name": "fn_get_square_root",
        "fn_args": {"a": 16.0},
    },
    {
        "prompt": "Substitute the digits in the string \"Hello 34 I'm 233 years old\" with 'NUMBERS'",
        "fn_name": "fn_substitute_string_with_regex",
        "fn_args": {
            "source_string": "Hello 34 I'm 233 years old",
            "regex": "\\d+",
            "replacement": "NUMBERS",
        },
    },
    {
        "prompt": "Replace all vowels in 'Programming is fun' with asterisks",
        "fn_name": "fn_substitute_string_with_regex",
        "fn_args": {
            "source_string": "Programming is fun",
            "regex": "[aeiouAEIOU]",
            "replacement": "*",
        },
    },
    {
        "prompt": "Substitute the word 'cat' with 'dog' in 'The cat sat on the mat with another cat'",
        "fn_name": "fn_substitute_string_with_regex",
        "fn_args": {
            "source_string": "The cat sat on the mat with another cat",
            "regex": "\\bcat\\b",
            "replacement": "dog",
        },
    },
    {
        "prompt": "Is 4 an even number?",
        "fn_name": "fn_is_even",
        "fn_args": {"n": 4},
    },
    {
        "prompt": "Is 7 an even number?",
        "fn_name": "fn_is_even",
        "fn_args": {"n": 7},
    },
    {
        "prompt": "What is the product of 3 and 5?",
        "fn_name": "fn_multiply_numbers",
        "fn_args": {"a": 3.0, "b": 5.0},
    },
    {
        "prompt": "What is the product of 12 and 4?",
        "fn_name": "fn_multiply_numbers",
        "fn_args": {"a": 12.0, "b": 4.0},
    },
]

FUNCTION_MAP = {
    "fn_add_numbers": fn_add_numbers,
    "fn_greet": fn_greet,
    "fn_multiply_numbers": fn_multiply_numbers,
    "fn_is_even": fn_is_even,
    "fn_substitute_string_with_regex": fn_substitute_string_with_regex,
    "fn_get_square_root": fn_get_square_root,
    "fn_reverse_string": fn_reverse_string,
}


def normalize_answer(item: dict) -> dict:
    fn_name = item.get("fn_name", item.get("name"))
    fn_args = item.get("args", item.get("parameters"))
    return {
        "prompt": item.get("prompt"),
        "fn_name": fn_name,
        "fn_args": fn_args,
    }


def evaluate(student_answers: list) -> None:
    correction_by_prompt = {ex["prompt"]: ex for ex in EXERCISES}

    total_score = 0
    checked = 0
    skipped = 0

    for raw_answer in student_answers:
        print("-" * 80)
        answer = normalize_answer(raw_answer)
        print(f"Prompt:  {answer['prompt']}")

        prompt = answer.get("prompt")
        if not isinstance(prompt, str):
            print("INVALID: missing prompt")
            continue

        correction = correction_by_prompt.get(prompt)
        if correction is None:
            skipped += 1
            print("SKIPPED: prompt not in exercises")
            continue

        checked += 1

        fn_name = answer.get("fn_name")
        fn_args = answer.get("fn_args")

        if not isinstance(fn_name, str):
            print("INVALID: wrong function name type")
            continue

        if not isinstance(fn_args, dict):
            print("INVALID: wrong function args type")
            continue

        if fn_name not in FUNCTION_MAP:
            print(f"INVALID: unknown function '{fn_name}'")
            continue

        fn = FUNCTION_MAP[fn_name]

        try:
            student_output = fn(**fn_args)
        except Exception as e:
            print(f"INVALID: error calling function: {e}")
            continue

        expected_output = correction["fn_name"]
        expected_fn = FUNCTION_MAP.get(correction["fn_name"])
        if expected_fn is None:
            continue
        expected_output = expected_fn(**correction["fn_args"])

        if student_output != expected_output:
            print(f"INVALID: output mismatch")
            print(f"  got:      {student_output}")
            print(f"  expected: {expected_output}")
            continue

        total_score += 1
        print(f"VALID ✓")

    print("-" * 80)
    print(f"Checked:     {checked}")
    print(f"Skipped:     {skipped}")
    print(f"Total score: {total_score}/{checked}")


def main() -> None:
    path = Path("data/output/function_calling_results.json")

    if len(sys.argv) > 1:
        path = Path(sys.argv[1])

    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        student_answers = json.load(f)

    if not isinstance(student_answers, list):
        print("ERROR: output file must be a JSON array")
        sys.exit(1)

    evaluate(student_answers)


if __name__ == "__main__":
    main()