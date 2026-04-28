from src.class_models import FunctionDefinition, TestPrompt
import json
from pydantic import ValidationError


class Parser:
    """Read and validate function definitions and test prompts from JSON."""

    def __init__(self, func_def_file: str, func_call_file: str) -> None:
        """Store input file paths for later parsing."""
        self.func_def_file = func_def_file
        self.func_call_file = func_call_file

    def read_valid_json(self, file: str) -> list[dict]:
        """Load a JSON array from a file and return an empty list on errors."""
        try:
            with open(file, 'r') as f:
                data: list[dict] = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError("Error:", e)
        except json.decoder.JSONDecodeError:
            raise Exception("Json data not valid.")
        except ValueError as e:
            raise ValueError("Error:", e)

        return data

    def read_func_def(self) -> list[FunctionDefinition]:
        """Parse and validate function definition objects."""

        data = self.read_valid_json(self.func_def_file)
        if not data:
            return []

        func_model_list: list[FunctionDefinition] = []
        for item in data:
            try:
                func_obj = FunctionDefinition(**item)
                func_model_list.append(func_obj)
            except ValidationError as e:
                print("Error in functions definition:", e.errors()[0]["msg"])
                raise
            except KeyError as e:
                raise ValueError("Error missing or incorrect key:", e)
        return func_model_list

    def read_func_call(self) -> list[TestPrompt]:
        """
            Parse and validate prompt objects
            used for function calling tests.
        """
        data = self.read_valid_json(self.func_call_file)
        if not data:
            return []

        test_model_list: list[TestPrompt] = []
        for item in data:
            try:
                test_obj = TestPrompt(**item)
                test_model_list.append(test_obj)
            except ValidationError as e:
                print("Error:", e.errors()[0]["msg"])
                raise
            except KeyError as e:
                raise ValueError("Error:", e)
        return test_model_list


if __name__ == "__main__":
    parser = Parser("input/functions_definition.json",
                    "input/function_calling_tests.json")
    list_def = parser.read_func_def()
    list_call = parser.read_func_call()
    print("First function from the json definitions file:\n", list_def[0])
    print("-" * 30)
    print("First prompt from the json calling file:\n", list_call[0])
