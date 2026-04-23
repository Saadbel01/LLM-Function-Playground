from src.class_models import FunctionDefinition
from collections import deque
import json
from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]
from src.parser import Parser


class Vocabulary:
    """Prepare token lookup tables used by constrained decoding."""

    def __init__(self, llm: Small_LLM_Model,
                 functions: list[FunctionDefinition]) -> None:
        """Load model vocabulary and precompute useful token tables."""
        vocab_path = llm.get_path_to_vocab_file()
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                vocab = json.load(f)
        except Exception as e:
            print("Error:", e)
            return
        self.id_to_token: dict[int, str] = {v: k for k, v in vocab.items()}
        self.token_to_id: dict[str, int] = vocab
        self.structural_tokens = self.get_structural_tokens()
        self.number_token_ids = self.get_number_token_ids()
        self.string_token_ids = self.get_string_tokens_ids()
        self.name_key_table = self.prefix_table(['"name"'])
        self.params_key_table = self.prefix_table(['"parameters"'])
        function_names = [func.name for func in functions]
        self.function_name_table = self.prefix_table(function_names)
        self.arg_key_tables = {}
        for func in functions:
            param_names = list(func.parameters.keys())
            self.arg_key_tables[func.name] = self.prefix_table(param_names)
        self.boolean_table = self.prefix_table(["true", "false"])

    def get_token_string(self, token_id: int) -> str:
        """Return token text from its ID."""
        return self.id_to_token[token_id]

    def get_token_id(self, token_string: str) -> int:
        """Return token ID from its text."""
        return self.token_to_id[token_string]

    def get_number_token_ids(self) -> list[int]:
        """Return token IDs that can compose numeric values."""
        valid_tokens = set("0123456789.-")
        token_ids = []
        for token, id_token in self.token_to_id.items():
            if all(tok in valid_tokens for tok in token):
                token_ids.append(id_token)
        return token_ids

    def get_string_tokens_ids(self) -> list[int]:
        """Return token IDs allowed for string value generation."""
        return [id_tok for token, id_tok in self.token_to_id.items()
                if '\n' not in token]

    def get_structural_tokens(self) -> dict[str, int]:
        """Return IDs for JSON structural characters used by the decoder."""
        structural_chars = ["{", "}", ":", ",", '"']
        return {char: self.token_to_id[char] for char in structural_chars}

    def prefix_table(self, valid_completations: list[str]) -> dict[str,
                                                                   list[int]]:
        """Build a prefix-to-valid-next-token-ID transition table."""
        queue = deque([""])
        table: dict[str, list[int]] = {}
        while queue:
            partial = queue.popleft()
            table[partial] = []
            for token, id_token in self.token_to_id.items():
                if token[:1].isspace():
                    continue
                candidate = partial + token
                if any(v_func.startswith(candidate)
                       for v_func in valid_completations):
                    table[partial].append(id_token)
                    if (not any(candidate == v_func
                                for v_func in valid_completations)
                            and candidate not in table
                            and candidate not in queue):
                        queue.append(candidate)
        return table


if __name__ == "__main__":
    llm = Small_LLM_Model()

    parser = Parser("input/functions_definition.json",
                    "input/function_calling_tests.json")
    functions = parser.read_func_def()

    vocab = Vocabulary(llm, functions)

    print(list(vocab.token_to_id.items())[:2])

    print(vocab.get_token_string(5519))
    print(vocab.get_token_id("{"))
    print(len(vocab.number_token_ids))
    print(len(vocab.string_token_ids))
    print(vocab.structural_tokens)
    print(vocab.function_name_table.keys())
