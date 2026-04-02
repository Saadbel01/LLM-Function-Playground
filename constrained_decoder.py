from enum import Enum
from vocabulary import Vocabulary
from class_models import FunctionDefinition


class Stage(Enum):
    NEED_OPEN_BRACE = "NEED_OPEN_BRACE"
    NEED_NAME_KEY = "NEED_NAME_KEY"
    NEED_COLON_1 = "NEED_COLON_1"
    NEED_QUOTE_OPEN_FUNC_NAME = "NEED_QUOTE_OPEN_FUNC_NAME"
    NEED_FUNC_NAME = "NEED_FUNC_NAME"
    NEED_QUOTE_CLOSE_FUNC_NAME = "NEED_QUOTE_CLOSE_FUNC_NAME"
    NEED_COMMA = "NEED_COMMA"
    NEED_PARAMS_KEY = "NEED_PARAMS_KEY"
    NEED_COLON_2 = "NEED_COLON_2"
    NEED_PARAMS_OPEN = "NEED_PARAMS_OPEN"
    NEED_QUOTE_OPEN_ARG_KEY = "NEED_QUOTE_OPEN_ARG_KEY"
    NEED_ARG_KEY = "NEED_ARG_KEY"
    NEED_QUOTE_CLOSE_ARG_KEY = "NEED_QUOTE_CLOSE_ARG_KEY"
    NEED_ARG_COLON = "NEED_ARG_COLON"
    NEED_QUOTE_OPEN_ARG_VALUE = "NEED_QUOTE_ARG_OPEN_VALUE"
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
        self.remaining_keys: set[str] = set()
        self.collected_args: dict[str, float | str | bool] = {}


class ConstrainedDecoder:

    def __init__(self, vocab: Vocabulary, functions: list[FunctionDefinition]):
        self.vocab = vocab
        self.functions = functions
        self.function_map = {fun.name: fun for fun in functions}
        self.function_names = set(self.function_map.keys())

    def get_function_param_type(self, state: DecoderState) -> str:
        return self.function_map[
            state.chosen_function
        ].parameters[state.current_arg].type

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

        elif state.current_stage.name.startswith("NEED_QUOTE"):
            return [self.vocab.structural_tokens['"']]

        elif state.current_stage == Stage.NEED_ARG_VALUE:
            param_type = self.get_function_param_type(state)
            if param_type == "number":
                valid = list(self.vocab.number_token_ids)

                # if there are more keys AFTER this one → allow comma
                if len(state.remaining_keys) > 1:
                    valid.append(self.vocab.structural_tokens[","])
                else:
                    valid.append(self.vocab.structural_tokens["}"])

                return valid
            elif param_type == "string":
                # print("STRING")
                return self.vocab.string_token_ids
            elif param_type == "boolean":
                return self.vocab.boolean_table[state.partial]

        elif state.current_stage == Stage.NEED_COMMA_OR_CLOSE:
            if len(state.remaining_keys) > 0:
                return [self.vocab.structural_tokens[',']]
            else:
                return [self.vocab.structural_tokens['}']]

        elif state.current_stage == Stage.NEED_CLOSE_OUTER:
            return [self.vocab.structural_tokens['}']]

        elif state.current_stage == Stage.DONE:
            return []
        else:
            raise ValueError(f"Unknown state: {state}")

    def update_state(self, state: DecoderState, token_id: int) -> None:
        token_string = self.vocab.get_token_string(token_id)
        if state.current_stage == Stage.NEED_OPEN_BRACE:
            if token_string == '{':
                state.current_stage = Stage.NEED_NAME_KEY
        elif state.current_stage == Stage.NEED_NAME_KEY:
            state.partial += token_string
            if state.partial == '"name"':
                state.partial = ""
                state.current_stage = Stage.NEED_COLON_1
        elif state.current_stage == Stage.NEED_COLON_1:
            if token_string == ":":
                state.current_stage = Stage.NEED_QUOTE_OPEN_FUNC_NAME
        elif state.current_stage == Stage.NEED_QUOTE_OPEN_FUNC_NAME:
            state.current_stage = Stage.NEED_FUNC_NAME
        elif state.current_stage == Stage.NEED_FUNC_NAME:
            state.partial += token_string
            if state.partial in self.function_names:
                state.chosen_function = state.partial
                state.remaining_keys = set(self.function_map[
                    state.chosen_function].parameters.keys())
                state.partial = ""
                state.current_stage = Stage.NEED_QUOTE_CLOSE_FUNC_NAME

        elif state.current_stage == Stage.NEED_QUOTE_CLOSE_FUNC_NAME:
            state.current_stage = Stage.NEED_COMMA

        elif state.current_stage == Stage.NEED_COMMA:
            if token_string == ",":
                state.current_stage = Stage.NEED_PARAMS_KEY
        elif state.current_stage == Stage.NEED_PARAMS_KEY:
            state.partial += token_string
            if state.partial == '"parameters"':
                state.partial = ""
                state.current_stage = Stage.NEED_COLON_2
        elif state.current_stage == Stage.NEED_COLON_2:
            if token_string == ":":
                state.current_stage = Stage.NEED_PARAMS_OPEN
        elif state.current_stage == Stage.NEED_PARAMS_OPEN:
            if token_string == "{":
                state.current_stage = Stage.NEED_QUOTE_OPEN_ARG_KEY

        elif state.current_stage == Stage.NEED_QUOTE_OPEN_ARG_KEY:
            state.current_stage = Stage.NEED_ARG_KEY

        elif state.current_stage == Stage.NEED_ARG_KEY:
            state.partial += token_string
            if state.partial in state.remaining_keys:
                state.current_arg = state.partial
                state.partial = ""
                state.current_stage = Stage.NEED_QUOTE_CLOSE_ARG_KEY

        elif state.current_stage == Stage.NEED_QUOTE_CLOSE_ARG_KEY:
            state.current_stage = Stage.NEED_ARG_COLON

        elif state.current_stage == Stage.NEED_ARG_COLON:
            if token_string == ":":
                param_type = self.get_function_param_type(state)
                if param_type == "number":
                    state.current_stage = Stage.NEED_ARG_VALUE
                else:
                    state.current_stage = Stage.NEED_QUOTE_OPEN_ARG_VALUE

        elif state.current_stage == Stage.NEED_QUOTE_OPEN_ARG_VALUE:
            state.current_stage = Stage.NEED_ARG_VALUE

        elif state.current_stage == Stage.NEED_ARG_VALUE:
            type_selected = self.get_function_param_type(state)
            # print("type:", type_selected)
            if type_selected == "number":
                if "," in token_string or "}" in token_string:
                    state.collected_args[state.current_arg] = float(
                        state.partial.replace("\u0120", "").strip())
                    state.used_keys.add(state.current_arg)
                    state.remaining_keys.discard(state.current_arg)
                    state.partial = ""
                    if "}" in token_string:
                        # print("this is for debugging")
                        if token_string.count('}') == 2:
                            state.current_stage = Stage.DONE
                        else:
                            state.current_stage = Stage.NEED_CLOSE_OUTER
                    elif "," in token_string:
                        # print("this is for debugging")
                        state.current_stage = Stage.NEED_QUOTE_OPEN_ARG_KEY
                else:
                    state.partial += token_string
            elif type_selected == "string":
                if '"' in token_string:
                    idx = token_string.find('"')
                    state.partial += token_string[:idx]
                    state.collected_args[state.current_arg] = state.partial.replace("\u0120", " ").strip()
                    state.used_keys.add(state.current_arg)
                    state.remaining_keys.discard(state.current_arg)
                    state.partial = ""
                    if '}' in token_string:
                        # print("this is for debugging")
                        if token_string.count('}') == 2:
                            state.current_stage = Stage.DONE
                        else:
                            state.current_stage = Stage.NEED_CLOSE_OUTER
                    else:
                        if "," in token_string:
                            state.current_stage = Stage.NEED_QUOTE_OPEN_ARG_KEY
                        else:
                            state.current_stage = Stage.NEED_COMMA_OR_CLOSE
                elif '}' in token_string:
                    state.collected_args[state.current_arg] = state.partial
                    state.used_keys.add(state.current_arg)
                    state.remaining_keys.discard(state.current_arg)
                    state.partial = ""
                    if token_string.count('}') == 2:
                        # print("this is for debugging")
                        state.current_stage = Stage.DONE
                    else:
                        state.current_stage = Stage.NEED_CLOSE_OUTER
                else:
                    state.partial += token_string
            elif type_selected == "boolean":
                state.partial += token_string
                if state.partial == "true" or state.partial == "false":
                    state.collected_args[state.current_arg] = (
                        state.partial == "true")
                    state.used_keys.add(state.current_arg)
                    state.remaining_keys.discard(state.current_arg)
                    state.partial = ""
                    state.current_stage = Stage.NEED_COMMA_OR_CLOSE
        elif state.current_stage == Stage.NEED_COMMA_OR_CLOSE:
            if token_string == ",":
                state.current_stage = Stage.NEED_QUOTE_OPEN_ARG_KEY
            elif "}" in token_string:
                if token_string.count('}') == 2:
                    state.current_stage = Stage.DONE
                else:
                    state.current_stage = Stage.NEED_CLOSE_OUTER
                state.current_stage = Stage.NEED_CLOSE_OUTER
        elif state.current_stage == Stage.NEED_CLOSE_OUTER:
            if token_string == "}":
                state.current_stage = Stage.DONE

    def mask_logits(self, state: DecoderState, logits) -> list[float]:

        valid_ids = self.get_valid_token_ids(state)
        masked = [float('-inf')] * len(logits)
        for i in valid_ids:
            masked[i] = logits[i]

        return masked


if __name__ == "__main__":
    stage = Stage("NEED_OPEN_BRACE")
    print(stage.value)
    print('"}}\n'.count('}'))
