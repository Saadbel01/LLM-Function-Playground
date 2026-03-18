from llm_sdk import Small_LLM_Model
import numpy as np
import json

model = Small_LLM_Model()


# Softmax
# def softmax(x):
#     e_x = np.exp(x - np.max(x))  # subtract max for numerical stability
#     return e_x / e_x.sum()


# prompt = "What is the sum of 4 and 2"
# initial_prompt = prompt

# top_token_id = 1
# count_token = 0

# while top_token_id != model._tokenizer.eos_token_id and count_token < 20:

#     text_encode = model.encode(prompt)

#     logits = model.get_logits_from_input_ids(text_encode[0].tolist())

#     # Convert to numpy array
#     logits_np = np.array(logits)

#     probs = softmax(logits_np)

#     # Top token
#     top_token_id = int(np.argmax(probs))
#     # top_prob = probs[top_token_id]
#     top_token_text = model.decode([top_token_id])
#     prompt += top_token_text
#     count_token += 1

# result = prompt[len(initial_prompt):]
# print("result :", result)

# print(f"Top token ID : {top_token_id}")
# print(f"Top token    : '{top_token_text}'")
# print(f"Probability  : {top_prob:.4f}")

# Top 5
# top5_ids = np.argsort(probs)[::-1][:5]
# for token_id in top5_ids:
#     print(f"'{model.decode([int(token_id)])}' → {probs[token_id]:.4f}")

# next_token_id = np.argmax(logits)

# print(dir(model))
vocab_path = model.get_path_to_vocab_file()
print(vocab_path)
with open(vocab_path, encoding="utf-8") as f:
    vocab = json.load(f)

print(type(vocab))
print(len(vocab))


print(list(vocab.items())[:10])  # first 20 entries
print(vocab["!"])
