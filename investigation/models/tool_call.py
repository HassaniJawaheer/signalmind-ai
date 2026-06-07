from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    tool_name: str
    tool_input: dict
    tool_output: Any