import json
from investigation.errors import InvestigationError
from investigation.models.agent_action import AgentAction


class OutputParser:

    def parse(self, output: str) -> AgentAction:
        try:
            data = json.loads(output)
        except (json.JSONDecodeError, TypeError) as error:
            raise InvestigationError("invalid_response", "The model response is not valid JSON.") from error

        if not isinstance(data, dict):
            raise InvestigationError("invalid_action", "The model response must be a JSON object.")

        action = AgentAction(
            action_type=data.get("action_type"),
            observations=data.get("observations", ""),
            hypotheses=data.get("hypotheses", ""),
            tool_name=data.get("tool_name"),
            tool_input=data.get("tool_input", {}),
            final_conclusion=data.get("final_conclusion"),
        )
        action.validate()
        return action
