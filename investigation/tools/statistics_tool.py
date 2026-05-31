import pandas as pd


class StatisticsTool:

    def compute(
        self,
        df: pd.DataFrame,
    ) -> dict:

        sensors = [
            "temperature",
            "vibration",
            "power_consumption",
            "machine_activity",
            "pressure",
            "flow_rate",
        ]

        results = {}

        for sensor in sensors:

            values = df[sensor]

            slope = (
                values.iloc[-1]
                - values.iloc[0]
            )

            results[sensor] = {
                "mean": float(values.mean()),
                "std": float(values.std()),
                "min": float(values.min()),
                "max": float(values.max()),
                "slope": float(slope),
            }

        return results