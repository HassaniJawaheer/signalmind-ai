from pathlib import Path

import pandas as pd

from config.settings import SENSORS
from investigation.tools.base_tool import BaseTool


class StatisticsTool(BaseTool):

    @property
    def name(self) -> str:
        return "statistics"

    @property
    def description(self) -> str:
        return "Compute statistics on sensor history."

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def run(self, timestamp: str, n_points: int = 100) -> dict:

        df = pd.read_csv(self.csv_path)

        index = df[df["timestamp"] == timestamp].index

        if len(index) == 0:
            raise ValueError(f"Timestamp {timestamp} not found.")

        end_idx = index[0]

        start_idx = max(0,end_idx - n_points)

        history_df = df.iloc[start_idx:end_idx + 1]

        results = {}

        for sensor in SENSORS:

            values = history_df[sensor]

            slope = values.iloc[-1] - values.iloc[0]

            results[sensor] = {
                "mean": float(values.mean()),
                "std": float(values.std()),
                "min": float(values.min()),
                "max": float(values.max()),
                "slope": float(slope),
            }

        return results