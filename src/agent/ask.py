import ollama

from agent.prompt import SYSTEM_PROMPT
from agent.tools import TOOLS, TOOL_FUNCTIONS
from config import MODEL, ENABLE_TOOLS

def ask(text):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]

    response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS if ENABLE_TOOLS else None)

    if response["message"].get("tool_calls"):
        messages.append(response["message"])
        for tool_call in response["message"]["tool_calls"]:
            name = tool_call["function"]["name"]
            args = tool_call["function"].get("arguments", {})
            result = TOOL_FUNCTIONS[name](**args)
            messages.append({"role": "tool", "content": str(result)})

        response = ollama.chat(model=MODEL, messages=messages)

    return response["message"]["content"].strip()
