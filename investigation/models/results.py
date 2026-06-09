from dataclasses import dataclass, field
from typing import List, Optional

from .request import Request
from .tool_call import ToolCall


@dataclass
class InvestigationResult:
    request: Request
    tool_calls: List[ToolCall] = field(default_factory=list)
    observations: List[str]
    hypotheses: List[str]
    final_conclusion: Optional[str] = None