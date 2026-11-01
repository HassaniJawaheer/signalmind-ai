from data.measurement_history import MeasurementHistory

from data.scenarios.factory_machine import Factory
from detection.detector import AnomalyDetector
from investigation.agents.llm_agent import LLMAgent
from investigation.models.context import Context
from investigation.models.request import Request
from investigation.runtime import InvestigationRuntime
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool
from investigation.tools.tool_registry import ToolRegistry


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

tool_registry = ToolRegistry()

tool_registry.register(HistoryTool(history=history))

tool_registry.register(StatisticsTool(history=history))

agent = LLMAgent(tool_registry=tool_registry)

runtime = InvestigationRuntime(agent=agent, registry=tool_registry)

print("\n========== AVAILABLE TOOLS ==========\n")

print(tool_registry.describe_tools())

print("\n========== REQUEST ==========\n")

print(request)

print("\n========== RUNTIME EXECUTION ==========\n")

result = runtime.run(context)

print("\n========== TOOL CALLS ==========\n")

for tool_call in result.tool_calls:
    print(tool_call.tool_name)

print("\n========== OBSERVATIONS ==========\n")

for observation in result.observations:

    print(observation)

print("\n========== HYPOTHESES ==========\n")

for hypothesis in result.hypotheses:

    print(hypothesis)

print("\n========== FINAL CONCLUSION ==========\n")

print(result.final_conclusion)

print("\n========== RESULT ==========\n")

print(result)
