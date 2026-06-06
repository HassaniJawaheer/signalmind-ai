from pathlib import Path

import pandas as pd

from data.scenarios.factory_machine import Factory

from detection.detector import AnomalyDetector

from investigation.models.request import Request
from investigation.models.results import InvestigationResult
from investigation.models.tools import Tool

from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool


N_STEPS = 10000

CSV_DIR = Path("experiments/outputs/csv")
CSV_DIR.mkdir(parents=True, exist_ok=True)

machine = Factory.create()

data = machine.run(
    n_steps=N_STEPS
)

external_df = pd.DataFrame(data)
external_df.to_csv(CSV_DIR / "simulation.csv", index=False)

detector = AnomalyDetector()

detections = []

for snapshot in data:

    detection = detector.detect(snapshot)

    if detection.trigger:
        detections.append(detection)

if not detections:
    raise RuntimeError("No anomaly detected.")

detection = detections[0]

print(f"Detection found at {detection.timestamp}")

request = Request(timestamp=detection.timestamp, sensor_values=detection.sensor_values)

history_tool = HistoryTool(csv_path=CSV_DIR / "simulation.csv")

history_df = history_tool.get_history(timestamp=request.timestamp, n_points=100)

print(f"History rows: {len(history_df)}")

statistics_tool = StatisticsTool()

statistics = statistics_tool.compute(history_df)

result = InvestigationResult(request=request)

result.tool_calls.append(
    Tool(
        tool_name="history_tool",
        tool_input={
            "timestamp": request.timestamp,
            "n_points": 100,
        },
        tool_output={
            "rows": len(history_df)
        }
    )
)

result.tool_calls.append(
    Tool(
        tool_name="statistics_tool",
        tool_input={},
        tool_output=statistics
    )
)

print("\n========== REQUEST ==========\n")
print(request)

print("\n========== STATISTICS ==========\n")

for sensor, values in statistics.items():

    print(sensor)

    for key, value in values.items():
        print(f"  {key}: {value}")

print("\n========== RESULT ==========\n")
print(result)