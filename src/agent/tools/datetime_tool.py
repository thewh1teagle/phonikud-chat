from datetime import datetime

SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_current_datetime",
        "description": "Get the current date and time",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


def execute(**_):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
