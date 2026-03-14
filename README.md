# Call_me_maybe

A small learning project to understand how Large Language Models (LLMs) work in practice, with a focus on:

- Constrained decoding
- Function calling
- Structured output from a Qwen ("Qween") model

## Why this project exists

This project is created for learning.

The main goal is to go deeper than simple chat responses and understand how to make an LLM produce outputs that software can execute safely and reliably.

## Core idea

LLMs are very good at understanding and generating human language.

But by default, they do not always return strict, machine-executable structures (like valid JSON with exact argument types).

Function calling + constrained decoding helps bridge this gap.

## Natural language vs function call

User request:

> "What is the sum of 40 and 2?"

Traditional LLM answer:

> "The sum of 40 and 2 is 42."

Function-calling style output:

```json
{
  "function": "add_numbers",
  "arguments": {
    "a": 40,
    "b": 2
  }
}
```

The model does not directly solve the task in free text.
It returns the right tool (`add_numbers`) and typed arguments (`a`, `b`) so your program can execute the function.

## What constrained decoding means here

Constrained decoding guides token generation so the model stays inside a required format, for example:

- valid JSON only
- allowed function names only
- correct argument structure and types

This reduces output errors and makes LLM behavior more reliable in applications.

## Where this is used

This pattern is common in:

- AI assistants that call tools (calculator, search, database)
- Workflow automation
- API orchestration
- Agent systems
- Production apps that need predictable, structured responses

## Project purpose (simple)

This repository is for experimentation and learning:

- understanding LLM internals and behavior
- practicing structured generation with Qwen
- testing how natural language is mapped to function calls
- exploring safe and deterministic execution flow
