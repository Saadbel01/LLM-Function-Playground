from class_models import FunctionDefinition


def build_prompt(prompt: str, functions: list[FunctionDefinition]) -> str:
    available_functions = ""
    for fun in functions:
        params = []
        for par_key, par_val in fun.parameters.items():
            params.append(f"{par_key}: {par_val.type}")
        available_functions += (f"- {fun.name}({", ".join(params)}) ->"
                                f" {fun.returns.type}: {fun.description}\n")
    return (
        f"<|im_start|>system\n"
        f"You are a function calling assistant. Given a user request,\n"
        f"select the appropriate function and extract the arguments.\n"
        f"Available functions:\n"
        f"{available_functions}"
        f"<|im_end|>\n"
        f"<|im_start|>user\n"
        f"{prompt}\n"
        f"<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


if __name__ == "__main__":
    from parser import Parser
    parser = Parser("input/functions_definition.json",
                    "input/function_calling_tests.json")
    list_def = parser.read_func_def()
    print(build_prompt("what is the sum of 40 and 2 ?", list_def))
