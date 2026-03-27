from constrained_decoder import DecoderState
from llm_sdk import Small_LLM_Model
from prompt_builder import build_prompt
from parser import Parser
from constrained_decoder import Stage, ConstrainedDecoder
import numpy as np
from vocabulary import Vocabulary


def main():

    model = Small_LLM_Model()
    state = DecoderState()
    generated_tokens = []
    parser = Parser("input/functions_definition.json",
                    "input/function_calling_tests.json")
    list_funcs = parser.read_func_def()
    prompt_tokens = model.encode(build_prompt("What is the sum of 2 and 3?",
                                              list_funcs))[0].tolist()
    vocab = Vocabulary(model, list_funcs)
    decoder = ConstrainedDecoder(vocab, list_funcs)

    while state.current_stage != Stage.DONE:
        all_tokens = prompt_tokens + generated_tokens
        logits = model.get_logits_from_input_ids(all_tokens)
        masked_logits = decoder.mask_logits(state, np.array(logits))
        token = int(np.argmax(masked_logits))
        generated_tokens.append(token)
        decoder.update_state(state, token)

    result = model.decode(generated_tokens)
    return result


if __name__ == "__main__":
    print(main())
