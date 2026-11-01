from config.settings import SENSORS
from data.measurement_history import MeasurementHistory
from investigation.tools.base_tool import BaseTool


class HistoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "history"

    @property
    def description(self) -> str:
        return (
            "Read recorded sensor measurements from the simulation JSONL. "
            "Parameters: timestamp (optional ISO 8601 with timezone), n_points "
            "(positive integer, default 100). Returns at most N measurements at or "
            "before timestamp, including it; omit timestamp for latest recorded data. "
            "For an inclusive time window, supply timestamp, before_seconds and "
            "optionally after_seconds (default 0); n_points is then ignored. "
            "Only available measurements are returned; inspect returned timestamps "
            "for actual coverage. An empty window returns empty lists."
        )

    def __init__(self, history: MeasurementHistory):
        self.history = history

    def run(self, timestamp: str | None = None, n_points: int = 100,
            before_seconds: float | None = None, after_seconds: float = 0) -> dict:
        rows = self.history.select(timestamp, n_points, before_seconds, after_seconds)
        return {key: [row[key] for row in rows] for key in [*SENSORS, "timestamp"]}
