from collections import deque
from datetime import datetime, timedelta, timezone
import json
from math import isfinite
from pathlib import Path
from uuid import uuid4

from config.settings import SENSORS


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
        """Latest N rows <= timestamp, or an inclusive temporal window.

        Window mode requires timestamp and before_seconds; n_points is ignored.
        Only recorded rows are returned, including for incomplete windows.
        Files must contain strictly increasing timestamps from a single run.
        """
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
        rows = [] if window else deque(maxlen=n_points)
        previous = None
        with self.path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                record = json.loads(line)
                instant = parse_timestamp(record["timestamp"])
                if previous is not None and instant <= previous:
                    raise ValueError(f"Non-increasing timestamp at line {line_number}.")
                previous = instant
                if (lower is None or instant >= lower) and (upper is None or instant <= upper):
                    rows.append(record)
        return list(rows)
