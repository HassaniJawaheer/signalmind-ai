from dataclasses import dataclass

@dataclass
class DetectionResult:
    anomaly: bool
    score: int
    reasons: list[str]