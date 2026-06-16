from pathlib import Path
import pandas as pd
from data.scenarios.factory_machine import Factory
from detection.detector import AnomalyDetector
from investigation.models.request import Request
from investigation.models.context import Context
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool
from investigation.tools.tool_registry import ToolRegistry
from investigation.agents.llm_agent import LLMAgent
from investigation.langgraph.nodes import initialize_nodes
from investigation.langgraph.graph import graph


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

registry.register(StatisticsTool(csv_path=CSV_DIR / "simulation.csv"))


agent = LLMAgent(tool_registry=registry)


initialize_nodes(
    llm_agent=agent,
    tool_registry=registry
)


print("\n========== REQUEST ==========\n")

print(request)


print("\n========== LANGGRAPH EXECUTION ==========\n")


result = graph.invoke(context)


print("\n========== FINAL STATE ==========\n")

print(result)