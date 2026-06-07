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
    
    def run(self, df: pd.DataFrame) -> dict:

        results = {}

        for sensor in SENSORS:
            values = df[sensor]
            slope = values.iloc[-1] - values.iloc[0]

            results[sensor] = {
                "mean": float(values.mean()),
                "std": float(values.std()),
                "min": float(values.min()),
                "max": float(values.max()),
                "slope": float(slope),
            }

        return results