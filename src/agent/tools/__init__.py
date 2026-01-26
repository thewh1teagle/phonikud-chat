from agent.tools.datetime_tool import SCHEMA as datetime_schema, execute as datetime_execute

TOOLS = [datetime_schema]

TOOL_FUNCTIONS = {
    "get_current_datetime": datetime_execute,
}
