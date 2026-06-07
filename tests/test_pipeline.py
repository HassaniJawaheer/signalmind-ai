from pathlib import Path
import pandas as pd
from data.scenarios.factory_machine import Factory
from detection.detector import AnomalyDetector
from investigation.models.context import Context
from investigation.models.request import Request
from investigation.models.results import InvestigationResult
from investigation.models.tool_call import ToolCall
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool
from investigation.tools.tool_registry import ToolRegistry


N_STEPS = 10000

CSV_DIR = Path("experiments/outputs/csv")
CSV_DIR.mkdir(parents=True, exist_ok=True)

machine = Factory.create()

data = machine.run(n_steps=N_STEPS)

external_df = pd.DataFrame(data)

external_df.to_csv(CSV_DIR / "simulation.csv",index=False)

detector = AnomalyDetector()

detections = []

for snapshot in data:

    detection = detector.detect(snapshot)

    if detection.trigger:
        detections.append(detection)

if not detections:
    raise RuntimeError("No anomaly detected.")

detection = detections[0]

request = Request(
    timestamp=detection.timestamp,
    sensor_values=detection.sensor_values
)

context = Context(request=request)

registry = ToolRegistry()

registry.register(HistoryTool(csv_path=CSV_DIR / "simulation.csv"))

registry.register(StatisticsTool())

print("\n========== AVAILABLE TOOLS ==========\n")

print(registry.describe_tools())

history_tool = registry.get("history")

history_df = history_tool.run(timestamp=request.timestamp, n_points=100)

context.tool_calls.append(
    ToolCall(
        tool_name="history",
        tool_input={
            "timestamp": request.timestamp,
            "n_points": 100,
        },
        tool_output={
            "rows": len(history_df)
        }
    )
)

statistics_tool = registry.get("statistics")

statistics = statistics_tool.run(history_df)

context.tool_calls.append(
    ToolCall(
        tool_name="statistics",
        tool_input={},
        tool_output=statistics
    )
)

result = InvestigationResult(
    request=context.request,
    tool_calls=context.tool_calls,
    final_conclusion=context.final_conclusion
)

print("\n========== REQUEST ==========\n")

print(context.request)

print("\n========== TOOL CALLS ==========\n")

print(context.tool_calls)

print("\n========== STATISTICS ==========\n")

for sensor, values in statistics.items():

    print(sensor)

    for key, value in values.items():

        print(f" {key}: {value}")

print("\n========== CONTEXT ==========\n")

print(context)

print("\n========== RESULT ==========\n")

print(result)