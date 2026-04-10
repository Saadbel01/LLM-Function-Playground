from src.constrained_decoder import DecoderState
from llm_sdk import Small_LLM_Model
from src.prompt_builder import build_prompt
from src.parser import Parser
from src.constrained_decoder import Stage, ConstrainedDecoder
import numpy as np
from src.vocabulary import Vocabulary
from src.class_models import FunctionCall
import json
import os



def main() -> list[FunctionCall]:

    model = Small_LLM_Model()
    state = DecoderState()
    parser = Parser("input/functions_definition.json",
                    "input/function_calling_tests.json")
    list_funcs = parser.read_func_def()
    list_call = parser.read_func_call()
    vocab = Vocabulary(model, list_funcs)
    decoder = ConstrainedDecoder(vocab, list_funcs)
    list_func_call = []
    count_same_token = 0
    list_stage = list(Stage)
    for prompt in list_call:
        print(prompt.prompt)
        generated_tokens = []
        prompt_tokens = model.encode(build_prompt(prompt.prompt,
                                                  list_funcs))[0].tolist()
        all_tokens = []
        previous_stage = state.current_stage

        while state.current_stage != Stage.DONE:
            update_done = False
            quote_forced = False
            if count_same_token >= 15:
                current_index = list_stage.index(state.current_stage)
                if current_index != Stage.DONE:
                    type_selected = decoder.get_function_param_type(state)
                    if type_selected == "number":
                        state.collected_args[state.current_arg] = float(
                            state.partial.replace("\u0120", "").strip())
                        state.used_keys.add(state.current_arg)
                        state.remaining_keys.discard(state.current_arg)
                        state.partial = ""
                        if len(state.remaining_keys) > 0:
                            state.current_stage = Stage.NEED_QUOTE_OPEN_ARG_KEY
                        else:
                            state.current_stage = Stage.NEED_CLOSE_OUTER
                    elif type_selected == "string":
                        quote_forced = True
                        state.collected_args[
                            state.current_arg] = state.partial.replace(
                                "\u0120", " ").strip()
                        state.used_keys.add(state.current_arg)
                        state.remaining_keys.discard(state.current_arg)
                        state.partial = ""
                        if len(state.remaining_keys) > 0:
                            state.current_stage = Stage.NEED_QUOTE_OPEN_ARG_KEY
                        else:
                            state.current_stage = Stage.NEED_CLOSE_OUTER
                    update_done = True

            all_tokens = prompt_tokens + generated_tokens
            previous_token = all_tokens[-1]
            logits = model.get_logits_from_input_ids(all_tokens)
            masked_logits = decoder.mask_logits(state, np.array(logits))
            if quote_forced:
                token = vocab.token_to_id['"}']
                quote_forced = False
            else:
                token = int(np.argmax(masked_logits))
            print_token = model.decode(token).rstrip("\n")
            if previous_stage == state.current_stage:
                if previous_token == token:
                    count_same_token += 1
                else:
                    count_same_token = 0
            else:
                count_same_token = 0
            previous_stage = state.current_stage
            print(print_token, end="", flush=True)
            generated_tokens.append(token)
            previous_stage = state.current_stage
            if not update_done:
                decoder.update_state(state, token)
        print()
        list_func_call.append(FunctionCall(prompt=prompt.prompt,
                                           name=state.chosen_function,
                                           parameters=state.collected_args))
        state.collected_args = {}
        state.current_stage = Stage.NEED_OPEN_BRACE
    return list_func_call


if __name__ == "__main__":
    try:
        list_call = main()
        os.makedirs("data/output", exist_ok=True)
        with open("data/output/function_calling_results.json",
                  "w", encoding="utf-8") as f:
            json.dump(
                [fc.model_dump() for fc in list_call],
                f,
                indent=2
            )
    except (KeyboardInterrupt, Exception) as e:
        print(e)
