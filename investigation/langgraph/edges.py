from investigation.models.context import Context


def should_continue(state: Context):

    if state.current_action.action_type == "call_tool":
        return "tool"
    return "end"