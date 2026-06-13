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
                observations=[],
                hypotheses=[],
            )

        if "statistics" not in context.working_memory:

            return AgentAction(
                action_type="call_tool",
                tool_name="statistics",
                tool_input={
                    "timestamp": context.request.timestamp,
                    "n_points": 100,
                },
                observations=[
                    "Historical sensor values have been retrieved."
                ],
                hypotheses=[],
            )

        return AgentAction(
            action_type="finish",
            tool_name=None,
            tool_input={},
            observations=[
                "Descriptive statistics have been computed."
            ],
            hypotheses=[
                "Cooling system degradation suspected."
            ],
            final_conclusion=(
                "Historical data and descriptive statistics "
                "suggest a cooling system degradation."
            ),
        )