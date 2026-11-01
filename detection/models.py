from dataclasses import dataclass


@dataclass
class Detection:
    trigger: bool
    score: int
    timestamp: str
    sensor_values: dict
