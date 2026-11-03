from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .request import Request
from .tool_call import ToolCall
from .agent_action import AgentAction


@dataclass
class Context:
    request: Request
    tool_calls: List[ToolCall] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    working_memory: Dict[str, Any] = field(default_factory=dict)
    final_conclusion: Optional[str] = None
    current_action: Optional[AgentAction] = None
    status: str = "running"
    stop_reason: Optional[str] = None
    error_message: Optional[str] = None
    iterations: int = 0
    observation_turns: List[int] = field(default_factory=list)
    hypothesis_turns: List[int] = field(default_factory=list)
