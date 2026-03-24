from enum import Enum
from vocabulary import Vocabulary
from class_models import FunctionDefinition


class Stage(Enum):
    NEED_OPEN_BRACE = "NEED_OPEN_BRACE"
    NEED_NAME_KEY = "NEED_NAME_KEY"
    NEED_COLON_1 = "NEED_COLON_1"
    NEED_FUNC_NAME = "NEED_FUNC_NAME"
    NEED_COMMA = "NEED_COMMA"
    NEED_PARAMS_KEY = "NEED_PARAMS_KEY"
    NEED_COLON_2 = "NEED_COLON_2"
    NEED_PARAMS_OPEN = "NEED_PARAMS_OPEN"
    NEED_ARG_KEY = "NEED_ARG_KEY"
    NEED_ARG_COLON = "NEED_ARG_COLON"
    NEED_ARG_VALUE = "NEED_ARG_VALUE"
    NEED_COMMA_OR_CLOSE = "NEED_COMMA_OR_CLOSE"
    NEED_CLOSE_OUTER = "NEED_CLOSE_OUTER"
    DONE = "DONE"


class DecoderState:

    def __init__(self):
        self.current_stage: Stage = Stage.NEED_OPEN_BRACE
        self.partial: str = ""
        self.chosen_function: str = ""
        self.current_arg: str = ""
        self.used_keys: set[str] = set()
        self.collected_args: dict[str, float | str | bool] = {}


class ConstrainedDecoder:

    def __init__(self, vocab: Vocabulary, functions: list[FunctionDefinition]):
        self.vocab = vocab
        self.functions = functions

    def get_function_param_type(self, state: DecoderState) -> str:
        for fun in self.functions:
            if fun.name == state.chosen_function:
                return fun.parameters[state.current_arg].type

    def get_remaining_keys(self, state: DecoderState) -> list[str]:
        for fun in self.functions:
            if fun.name == state.chosen_function:
                remaining = [k for k in fun.parameters.keys()
                             if k not in state.used_keys]
                break
        return remaining

    def get_valid_token_ids(self, state: DecoderState) -> list[int | None]:

        if state.current_stage == Stage.NEED_OPEN_BRACE:
            return [self.vocab.structural_tokens['{']]

        elif state.current_stage == Stage.NEED_NAME_KEY:
            return self.vocab.name_key_table[state.partial]

        elif state.current_stage == Stage.NEED_COLON_1:
            return [self.vocab.structural_tokens[':']]

        elif state.current_stage == Stage.NEED_FUNC_NAME:
            return self.vocab.function_name_table[state.partial]

        elif state.current_stage == Stage.NEED_COMMA:
            return [self.vocab.structural_tokens[',']]

        elif state.current_stage == Stage.NEED_PARAMS_KEY:
            return self.vocab.params_key_table[state.partial]

        elif state.current_stage == Stage.NEED_COLON_2:
            return [self.vocab.structural_tokens[':']]

        elif state.current_stage == Stage.NEED_PARAMS_OPEN:
            return [self.vocab.structural_tokens['{']]

        elif state.current_stage == Stage.NEED_ARG_KEY:
            return (
                self.vocab.arg_key_tables[state.chosen_function][state.partial]
                )

        elif state.current_stage == Stage.NEED_ARG_COLON:
            return [self.vocab.structural_tokens[':']]

        elif state.current_stage == Stage.NEED_ARG_VALUE:
            param_type = self.get_function_param_type(state)
            if param_type == "number":
                return (self.vocab.number_token_ids +
                        [self.vocab.structural_tokens[","]] +
                        [self.vocab.structural_tokens["}"]])
            elif param_type == "string":
                return self.vocab.string_token_ids
            elif param_type == "boolean":
                return self.vocab.boolean_table[state.partial]

        elif state.current_stage == Stage.NEED_COMMA_OR_CLOSE:
            remaining = self.get_remaining_keys(state)
            if len(remaining) > 0:
                return [self.vocab.structural_tokens[',']]
            else:
                return [self.vocab.structural_tokens['}']]

        elif state.current_stage == Stage.NEED_CLOSE_OUTER:
            return [self.vocab.structural_tokens['}']]

        elif state.current_stage == Stage.DONE:
            return []
        else:
            raise ValueError(f"Unknown state: {state}")

    def update_state(self, state: DecoderState) -> None:
        if state.current_stage == "NEED_OPEN_BRACE":
            state.current_stage = Stage.NEED_NAME_KEY
        elif state.current_stage == "NEED_NAME_KEY":
            


if __name__ == "__main__":
    stage = Stage("NEED_OPEN_BRACE")
    print(stage.value)
