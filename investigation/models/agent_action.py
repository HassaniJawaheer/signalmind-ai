from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class AgentAction:
    action_type: str
    observations: List[str]
    hypotheses: List[str]
    tool_name: Optional[str] = None
    tool_input: Dict = field(default_factory=dict)
    final_conclusion: Optional[str] = None