import json
from investigation.models.agent_action import AgentAction


class OutputParser:

    def parse(self,output: str) -> AgentAction:

        try:
            data = json.loads(output)

        except json.JSONDecodeError as e:

            raise ValueError(f"The LLM response is not valid JSON: {e}")

        return AgentAction(
            action_type=data["action_type"],
            observations=data.get(
                "observations",
                ""
            ),
            hypotheses=data.get(
                "hypotheses",
                ""
            ),
            tool_name=data.get(
                "tool_name"
            ),
            tool_input=data.get(
                "tool_input",
                {}
            ),
            final_conclusion=data.get(
                "final_conclusion"
            )
        )