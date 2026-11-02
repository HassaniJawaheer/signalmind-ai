from data.measurement_history import MeasurementHistory
from data.scenarios.factory_machine import Factory
from detection.detector import AnomalyDetector
from investigation.models.request import Request
from investigation.models.context import Context
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool
from investigation.tools.tool_registry import ToolRegistry
from investigation.agents.llm_agent import LLMAgent
from investigation.langgraph.graph import run_investigation


N_STEPS = 10000
history = MeasurementHistory.create()
print(f"Measurement history: {history.path}")
machine = Factory.create()

detector = AnomalyDetector()

detections = []


for _ in range(N_STEPS):
    snapshot = machine.step()
    history.append(snapshot)
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

registry.register(HistoryTool(history=history))

registry.register(StatisticsTool(history=history))


agent = LLMAgent(tool_registry=registry)


print("\n========== REQUEST ==========\n")

print(request)


print("\n========== LANGGRAPH EXECUTION ==========\n")


result = run_investigation(context, agent, registry)


print("\n========== FINAL STATE ==========\n")

print(result)
