from investigation.models.agent_action import AgentAction
from investigation.models.context import Context


class FakeAgent:
    
    def decide(self, context: Context) -> AgentAction:

        executed_tools = {
            tool_call.tool_name
            for tool_call in context.tool_calls
        }

        if "history" not in executed_tools:

            return AgentAction(
                action_type="call_tool",
                tool_name="history",
                tool_input={
                    "timestamp": context.request.timestamp,
                    "n_points": 100,
                },
            )

        if "statistics" not in executed_tools:

            return AgentAction(
                action_type="call_tool",
                tool_name="statistics",
                tool_input={},
            )

        return AgentAction(
            action_type="finish",
            final_conclusion=(
                "Historical data and descriptive statistics "
                "have been collected. Investigation completed."
            ),
        )