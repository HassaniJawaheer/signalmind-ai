from pathlib import Path
import pandas as pd
from investigation.tools.base_tool import BaseTool


class HistoryTool(BaseTool):
  
    @property
    def name(self) -> str:
        return "history"

    @property
    def description(self) -> str:
        return "Retrieve historical sensor values before a timestamp."
    
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def run(self, timestamp: str, n_points: int = 100) -> pd.DataFrame:
        df = pd.read_csv(self.csv_path)

        index = df[df["timestamp"] == timestamp].index

        if len(index) == 0:
            raise ValueError(f"Timesstamp {timestamp} not found.")
        
        end_idx = index[0]

        start_idx = max(0, end_idx - n_points)

        return df.iloc[start_idx:end_idx+1]