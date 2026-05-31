from dataclasses import dataclass
from typing import Dict


@dataclass
class Request:
    timestamp: str
    sensor_values: Dict[str, float]