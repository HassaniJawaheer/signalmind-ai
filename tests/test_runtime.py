from pathlib import Path
import pandas as pd

from data.scenarios.factory_machine import Factory
from detection.detector import AnomalyDetector
from investigation.agents.fake_agent import FakeAgent
from investigation.models.context import Context
from investigation.models.request import Request
from investigation.runtime import InvestigationRuntime
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool
from investigation.tools.tool_registry import ToolRegistry


N_STEPS = 10000

CSV_DIR = Path("experiments/outputs/csv")
CSV_DIR.mkdir(parents=True, exist_ok=True)

machine = Factory.create()

data = machine.run(n_steps=N_STEPS)

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

request = Request(
    timestamp=detection.timestamp,
    sensor_values=detection.sensor_values
)

context = Context(request=request)

registry = ToolRegistry()

registry.register(HistoryTool(csv_path=CSV_DIR / "simulation.csv"))
registry.register(StatisticsTool())

agent = FakeAgent()

runtime = InvestigationRuntime(
    agent=agent,
    registry=registry
)

print("\n========== AVAILABLE TOOLS ==========\n")

print(registry.describe_tools())

print("\n========== REQUEST ==========\n")

print(request)

print("\n========== RUNTIME EXECUTION ==========\n")

result = runtime.run(context)

print("\n========== TOOL CALLS ==========\n")

for tool_call in result.tool_calls:

    print(tool_call.tool_name)
    print(tool_call.tool_input)
    print(type(tool_call.tool_output))

print("\n========== CONTEXT ==========\n")

print(context)

print("\n========== RESULT ==========\n")

print(result)