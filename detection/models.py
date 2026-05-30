from dataclasses import dataclass


@dataclass
class Detection:

    trigger: bool

    score: int

    timestamp: int

    sensor_values: dict