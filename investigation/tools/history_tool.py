from config import settings
from data.measurement_history import MeasurementHistory
from investigation.tools.base_tool import BaseTool


class HistoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "history"

    @property
    def description(self) -> str:
        return (
            f"Retrieve raw measurements for 1 to {settings.MAX_HISTORY_SENSORS} sensors. "
            f"Required sensors: a list from {settings.SENSORS}. "
            f"n_points defaults to {settings.MAX_HISTORY_POINTS}; returns at most "
            f"{settings.MAX_HISTORY_POINTS} latest points per sensor. "
            "timestamp: optional timezone-aware ISO 8601 cutoff; use the alert timestamp. "
            "Alternatively supply timestamp, before_seconds and optional after_seconds=0 "
            "for an inclusive window (n_points then ignored). "
            "window reports actual coverage and truncation; earlier points may be omitted."
        )

    def __init__(self, history: MeasurementHistory):
        self.history = history

    def run(self, sensors: list[str], timestamp: str | None = None, n_points: int | None = None,
            before_seconds: float | None = None, after_seconds: float = 0) -> dict:
        if not isinstance(sensors, list) or not 1 <= len(sensors) <= settings.MAX_HISTORY_SENSORS:
            raise ValueError("Select one or two sensors within the configured limit.")
        if any(sensor not in settings.SENSORS for sensor in sensors):
            raise ValueError("Unknown sensor.")
        if len(set(sensors)) != len(sensors):
            raise ValueError("Sensors must be unique.")
        limit = settings.MAX_HISTORY_POINTS
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("MAX_HISTORY_POINTS must be a positive integer.")
        if n_points is None:
            n_points = limit
        rows, metadata = self.history.select_with_metadata(
            timestamp, n_points, before_seconds, after_seconds
        )
        rows = rows[-limit:]
        metadata.update({
            "count": len(rows),
            "truncated": metadata["selected_count"] > len(rows),
            "start": rows[0]["timestamp"] if rows else None,
            "end": rows[-1]["timestamp"] if rows else None,
        })
        result = {"window": metadata}
        for key in [*sensors, "timestamp"]:
            result[key] = [row[key] for row in rows]
        return result
