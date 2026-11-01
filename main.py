from data.measurement_history import MeasurementHistory
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




def main():

    machine = Factory.create()
    history = MeasurementHistory.create()
    print(f"Measurement history: {history.path}")

    detector = AnomalyDetector()

    registry = ToolRegistry()

    registry.register(HistoryTool(history=history))

    registry.register(StatisticsTool(history=history))

    agent = LLMAgent(tool_registry=registry)

    initialize_nodes(
        llm_agent=agent,
        tool_registry=registry
    )

    print("\nSignalMind AI started.\n")

    while True:

        sensors = machine.step()
        history.append(sensors)

        signal = detector.detect(
            sensor_values=sensors
        )

        if not signal.trigger:

            continue

        print("\n========== ANOMALY DETECTED ==========\n")

        request = Request(
            timestamp=signal.timestamp,
            sensor_values=signal.sensor_values
        )

        context = Context(request=request)

        result = graph.invoke(context)

        print("\n========== INVESTIGATION FINISHED ==========\n")

        print(
            f"Final conclusion:\n"
            f"{result.final_conclusion}"
        )

        print("\nObservations:\n")

        for observation in result.observations:

            print(f"- {observation}")

        print("\nHypotheses:\n")

        for hypothesis in result.hypotheses:

            print(f"- {hypothesis}")
        break

if __name__ == "__main__":

    main()
