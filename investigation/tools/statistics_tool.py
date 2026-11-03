from statistics import mean, stdev

from config.settings import SENSORS
from data.measurement_history import MeasurementHistory
from investigation.tools.base_tool import BaseTool
from config import settings


class StatisticsTool(BaseTool):
    @property
    def name(self) -> str:
        return "statistics"

    @property
    def description(self) -> str:
        return (
            "Compute mean, sample std (null for a single measurement), min, max "
            "and delta (last value minus first value, not a rate of change). "
            "Includes actual window count, start and end. "
            f"Analyzes at most {settings.MAX_ANALYSIS_POINTS} latest measurements locally. "
            "Parameters: timestamp (optional timezone-aware ISO 8601 cutoff), n_points=100. "
            "For an inclusive window use timestamp, before_seconds, after_seconds=0; "
            "n_points is then ignored. window reports actual coverage and truncation."
        )

    def __init__(self, history: MeasurementHistory):
        self.history = history

    def run(self, timestamp: str | None = None, n_points: int = 100,
            before_seconds: float | None = None, after_seconds: float = 0) -> dict:
        rows, metadata = self.history.select_with_metadata(
            timestamp, n_points, before_seconds, after_seconds
        )
        results = {"window": metadata}
        for sensor in SENSORS:
            values = [row[sensor] for row in rows]
            results[sensor] = {
                "mean": mean(values) if values else None,
                "std": stdev(values) if len(values) > 1 else None,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "delta": values[-1] - values[0] if values else None,
            }
        return results
