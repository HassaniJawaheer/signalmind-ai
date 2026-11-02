from investigation.models.context import Context


def should_continue(state: Context):
    if state.status != "running":
        return "finalize"
    if state.current_action.action_type == "call_tool":
        return "tool"
    return "finalize"


def after_tool(state: Context):
    if state.status != "running":
        return "finalize"
    return "llm"
