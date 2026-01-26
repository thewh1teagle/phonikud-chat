import ollama

from agent.prompt import SYSTEM_PROMPT


def ask(text):
    response = ollama.chat(
        model="gemma3:4b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return response["message"]["content"].strip()
