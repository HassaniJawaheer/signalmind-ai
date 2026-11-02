from dataclasses import dataclass, field
from typing import Dict, Optional
from investigation.errors import InvestigationError


@dataclass
class AgentAction:
    action_type: str
    observations: str
    hypotheses: str
    tool_name: Optional[str] = None
    tool_input: Dict = field(default_factory=dict)
    final_conclusion: Optional[str] = None

    def validate(self) -> None:
        valid = self.action_type in ("call_tool", "finish")
        valid = valid and isinstance(self.observations, str)
        valid = valid and isinstance(self.hypotheses, str)
        valid = valid and isinstance(self.tool_input, dict)

        if not valid:
            raise InvestigationError("invalid_action", "The agent returned an invalid action.")

        if self.action_type == "call_tool":
            if not isinstance(self.tool_name, str) or not self.tool_name.strip():
                raise InvestigationError("invalid_action", "A tool action requires a tool name.")
            if not all(isinstance(key, str) for key in self.tool_input):
                raise InvestigationError("invalid_action", "Tool parameter names must be strings.")
            if self.final_conclusion is not None:
                raise InvestigationError("invalid_action", "A tool action cannot contain a final conclusion.")

        if self.action_type == "finish":
            if not isinstance(self.final_conclusion, str) or not self.final_conclusion.strip():
                raise InvestigationError("invalid_action", "A finish action requires a conclusion.")
            if self.tool_name is not None or self.tool_input:
                raise InvestigationError("invalid_action", "A finish action cannot request a tool.")
