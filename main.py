from constrained_decoder import DecoderState
from llm_sdk import Small_LLM_Model
from prompt_builder import build_prompt
from parser import Parser
from constrained_decoder import Stage, ConstrainedDecoder
import numpy as np
from vocabulary import Vocabulary
from class_models import TestPrompt, FunctionCall
import json


def main():

    model = Small_LLM_Model()
    state = DecoderState()
    parser = Parser("input/functions_definition.json",
                    "input/function_calling_tests.json")
    list_funcs = parser.read_func_def()
    list_call = parser.read_func_call()
    # list_call = [TestPrompt(prompt="Substitute the word 'cat'
    # with 'dog' in 'The cat sat on the mat with another cat'")]
    vocab = Vocabulary(model, list_funcs)
    decoder = ConstrainedDecoder(vocab, list_funcs)
    list_func_call = []

    for prompt in list_call:
        print(prompt.prompt)
        generated_tokens = []
        prompt_tokens = model.encode(build_prompt(prompt.prompt,
                                                  list_funcs))[0].tolist()
        all_tokens = []
        while state.current_stage != Stage.DONE:
            all_tokens = prompt_tokens + generated_tokens
            logits = model.get_logits_from_input_ids(all_tokens)
            masked_logits = decoder.mask_logits(state, np.array(logits))
            token = int(np.argmax(masked_logits))
            print(model.decode(token).rstrip("\n"), end="", flush=True)
            # print(f"{state.current_stage.name}: [{model.decode(token)}]",
            # flush=True)
            generated_tokens.append(token)
            decoder.update_state(state, token)
        print()
        list_func_call.append(FunctionCall(prompt=prompt.prompt,
                                           name=state.chosen_function,
                                           parameters=state.collected_args))
        state.collected_args = {}
        state.current_stage = Stage.NEED_OPEN_BRACE
        # result = model.decode(generated_tokens)
    return list_func_call


# def simple_generation():
#     model = Small_LLM_Model()
#     path_tokenizer = model.get_path_to_tokenizer_file()
#     with open(path_tokenizer, 'r') as f:
#         tokenizer = json.load(f)
#     print(tokenizer["<|im_end|>"])
#     prompt = "Reverse a string and return the reversed result."
#     token = 0
#     print()
#     while token != 151643:
#         encoded_prompt = model.encode(prompt)
#         logits = model.get_logits_from_input_ids(encoded_prompt[0].tolist())
#         token = int(np.argmax(logits))
#         decoded_token = model.decode(token)
#         print(decoded_token, end="",  flush=True)
#         prompt += decoded_token


if __name__ == "__main__":
    try:
        list_call = main()

        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(
                [fc.model_dump() for fc in list_call],
                f,
                indent=2
            )
    except (KeyboardInterrupt):
        print("OK")
