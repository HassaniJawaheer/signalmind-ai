from dataclasses import dataclass
import datetime


@dataclass
class Detection:

    trigger: bool

    score: int

    timestamp: datetime.datetime

    sensor_values: dict