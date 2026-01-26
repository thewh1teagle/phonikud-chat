from agent.tools.datetime_tool import SCHEMA as datetime_schema, execute as datetime_execute
from agent.tools.voice_tool import SCHEMA as voice_schema, execute as voice_execute
from agent.tools.schedule_tool import (
    SCHEDULE_SCHEMA, LIST_SCHEMA, CANCEL_SCHEMA, TASK_SCHEMA,
    schedule_execute, list_execute, cancel_execute, task_execute,
)

TOOLS = [datetime_schema, voice_schema, SCHEDULE_SCHEMA, TASK_SCHEMA, LIST_SCHEMA, CANCEL_SCHEMA]

TOOL_FUNCTIONS = {
    "get_current_datetime": datetime_execute,
    "set_voice": voice_execute,
    "schedule_reminder": schedule_execute,
    "schedule_task": task_execute,
    "list_reminders": list_execute,
    "cancel_reminder": cancel_execute,
}
