import ollama

from agent.prompt import SYSTEM_PROMPT
from agent.tools import TOOLS, TOOL_FUNCTIONS


def ask(text):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]

    response = ollama.chat(model="qwen3:4b", messages=messages, tools=TOOLS)

    if response["message"].get("tool_calls"):
        messages.append(response["message"])
        for tool_call in response["message"]["tool_calls"]:
            name = tool_call["function"]["name"]
            args = tool_call["function"].get("arguments", {})
            result = TOOL_FUNCTIONS[name](**args)
            messages.append({"role": "tool", "content": str(result)})

        response = ollama.chat(model="qwen3:4b", messages=messages, think='low')

    return response["message"]["content"].strip()
