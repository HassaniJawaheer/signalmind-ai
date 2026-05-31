from dataclasses import dataclass
from typing import Any


@dataclass
class Tool:
    tool_name: str
    tool_input: dict
    tool_output: Any