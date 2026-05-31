from pathlib import Path
import pandas as pd


class HistoryTool:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def get_history(
        self,
        timestamp: str,
        n_points: int = 100,
    ) -> pd.DataFrame:

        df = pd.read_csv(self.csv_path)

        index = df[df["timestamp"] == timestamp].index

        if len(index) == 0:
            raise ValueError(f"Timestamp {timestamp} not found.")

        end_idx = index[0]
        start_idx = max(0, end_idx - n_points)

        return df.iloc[start_idx:end_idx + 1]