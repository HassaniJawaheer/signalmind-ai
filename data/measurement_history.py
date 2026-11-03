from collections import deque
from datetime import datetime, timedelta, timezone
import json
from math import isfinite
from pathlib import Path
from uuid import uuid4

from config.settings import SENSORS
from config import settings


def parse_timestamp(value: str) -> datetime:
    instant = datetime.fromisoformat(value)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone.")
    return instant.astimezone(timezone.utc)


class MeasurementHistory:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    @classmethod
    def create(cls, directory: str | Path = "experiments/outputs/jsonl"):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"simulation_{uuid4().hex}.jsonl"
        path.touch(exist_ok=False)
        return cls(path)

    def append(self, measurement: dict) -> None:
        record = dict(measurement)
        record["timestamp"] = parse_timestamp(record["timestamp"]).isoformat()
        for sensor in SENSORS:
            value = record[sensor]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError(f"Invalid measurement for {sensor}.")
        line = json.dumps(record, allow_nan=False) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Closing the file flushes the line before detection or tool reads.
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(line)

    def select(self, timestamp: str | None = None, n_points: int = 100,
               before_seconds: float | None = None, after_seconds: float = 0) -> list[dict]:
        rows, _ = self.select_with_metadata(timestamp, n_points, before_seconds, after_seconds)
        return rows

    def select_with_metadata(self, timestamp: str | None = None, n_points: int = 100,
                             before_seconds: float | None = None, after_seconds: float = 0):
        limit = settings.MAX_ANALYSIS_POINTS
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("MAX_ANALYSIS_POINTS must be a positive integer.")
        if isinstance(n_points, bool) or not isinstance(n_points, int) or n_points <= 0:
            raise ValueError("n_points must be a positive integer.")
        anchor = parse_timestamp(timestamp) if timestamp is not None else None
        window = before_seconds is not None
        for value in (before_seconds, after_seconds):
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                      or not isfinite(value) or value < 0):
                raise ValueError("Window durations must be finite non-negative seconds.")
        if window and anchor is None:
            raise ValueError("A temporal window requires timestamp.")
        if not window and after_seconds != 0:
            raise ValueError("after_seconds requires before_seconds.")
        lower = anchor - timedelta(seconds=before_seconds) if window else None
        upper = anchor + timedelta(seconds=after_seconds) if window else anchor
        capacity = limit
        if not window:
            capacity = min(n_points, limit)
        rows = deque(maxlen=capacity)
        matching_count = 0
        previous = None
        with self.path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                record = json.loads(line)
                instant = parse_timestamp(record["timestamp"])
                if previous is not None and instant <= previous:
                    raise ValueError(f"Non-increasing timestamp at line {line_number}.")
                previous = instant
                if (lower is None or instant >= lower) and (upper is None or instant <= upper):
                    matching_count += 1
                    rows.append(record)
        selected_count = matching_count
        if not window:
            selected_count = min(n_points, matching_count)
        rows = list(rows)
        metadata = {
            "selected_count": selected_count,
            "count": len(rows),
            "truncated": selected_count > len(rows),
            "start": rows[0]["timestamp"] if rows else None,
            "end": rows[-1]["timestamp"] if rows else None,
            "selection": "latest available points within requested bounds",
        }
        return rows, metadata
