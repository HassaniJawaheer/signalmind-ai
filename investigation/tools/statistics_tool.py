from statistics import mean, stdev

from config.settings import SENSORS
from data.measurement_history import MeasurementHistory
from investigation.tools.base_tool import BaseTool
from investigation.tools.history_tool import HistoryTool


class StatisticsTool(BaseTool):
    @property
    def name(self) -> str:
        return "statistics"

    @property
    def description(self) -> str:
        return (
            "Compute mean, sample std (null for a single measurement), min, max "
            "and slope (legacy name for last minus first, not a time-normalized slope). "
            "Includes actual window count, start and end. "
            + HistoryTool(self.history).description
        )

    def __init__(self, history: MeasurementHistory):
        self.history = history

    def run(self, timestamp: str | None = None, n_points: int = 100,
            before_seconds: float | None = None, after_seconds: float = 0) -> dict:
        rows = self.history.select(timestamp, n_points, before_seconds, after_seconds)
        results = {"window": {
            "count": len(rows),
            "start": rows[0]["timestamp"] if rows else None,
            "end": rows[-1]["timestamp"] if rows else None,
        }}
        for sensor in SENSORS:
            values = [row[sensor] for row in rows]
            results[sensor] = {
                "mean": mean(values) if values else None,
                "std": stdev(values) if len(values) > 1 else None,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "slope": values[-1] - values[0] if values else None,
            }
        return results
