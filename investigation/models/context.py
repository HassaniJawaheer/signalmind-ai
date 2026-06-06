from dataclasses import dataclass, field
from typing import List, Optional
from .request import Request
from .tools import Tool


@dataclass
class Context:
    request: Request
    tool_calls: List[Tool] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    hypotheses: List[str] = field(default_factory=list)
    final_conclusion: Optional[str] = None