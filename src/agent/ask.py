import ollama

from agent.prompt import SYSTEM_PROMPT
from agent.tools import TOOLS, TOOL_FUNCTIONS
from config import MODEL, ENABLE_TOOLS

MAX_TOOL_ROUNDS = 3


def ask(text, exclude_tools=None, system_prompt=None):
    messages = [
        {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]

    if not ENABLE_TOOLS:
        tools = None
    elif exclude_tools:
        tools = [t for t in TOOLS if t["function"]["name"] not in exclude_tools]
    else:
        tools = TOOLS

    for _ in range(MAX_TOOL_ROUNDS):
        response = ollama.chat(model=MODEL, messages=messages, tools=tools)

        if not response["message"].get("tool_calls"):
            break

        messages.append(response["message"])
        for tool_call in response["message"]["tool_calls"]:
            name = tool_call["function"]["name"]
            args = tool_call["function"].get("arguments", {})
            print(f"[tool] {name}({args})")
            result = TOOL_FUNCTIONS[name](**args)
            print(f"[tool] {name} -> {result}")
            messages.append({"role": "tool", "content": str(result)})

    return response["message"]["content"].strip()
