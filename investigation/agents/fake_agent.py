from investigation.models.agent_action import AgentAction
from investigation.models.context import Context


class FakeAgent:

    def decide(self, context: Context) -> AgentAction:

        if "history" not in context.working_memory:

            return AgentAction(
                action_type="call_tool",
                tool_name="history",
                tool_input={
                    "timestamp": context.request.timestamp,
                    "n_points": 100,
                },
            )

        if "statistics" not in context.working_memory:

            return AgentAction(
                action_type="call_tool",
                tool_name="statistics",
                tool_input={
                    "df": context.working_memory["history"]
                },
            )

        return AgentAction(
            action_type="finish",
            final_conclusion=(
                "Historical data and descriptive statistics "
                "have been collected. Investigation completed."
            ),
        )