from investigation.models.context import Context
from investigation.models.request import Request
from investigation.models.tool_call import ToolCall
from investigation.agents.prompt_builder import PromptBuilder
from investigation.tools.tool_registry import ToolRegistry
from investigation.tools.history_tool import HistoryTool
from investigation.tools.statistics_tool import StatisticsTool


request = Request(
    timestamp="2026-06-13 15:00:00",
    sensor_values={
        "temperature": 119.8,
        "vibration": 0.99,
        "pressure": 0.24,
        "flow_rate": 0.51
    }
)

context = Context(request=request)

context.observations.extend(
    [
        "Historical sensor values have been retrieved.",
        "Temperature is increasing."
    ]
)

context.hypotheses.extend(["Cooling system degradation suspected."])

context.tool_calls.extend(
    [
        ToolCall(
            tool_name="history",
            tool_input={
                "timestamp": request.timestamp,
                "n_points": 10
            },
            tool_output={
                "temperature": [95.2, 101.3, 108.4, 119.8]
            }
        ),
        ToolCall(
            tool_name="statistics",
            tool_input={
                "timestamp": request.timestamp,
                "n_points": 10
            },
            tool_output={
                "temperature": {
                    "mean": 106.2,
                    "std": 8.7,
                    "slope": 24.6
                }
            }
        )
    ]
)

tool_registry = ToolRegistry()

tool_registry.register(HistoryTool(csv_path="dummy.csv"))

tool_registry.register(StatisticsTool(csv_path="dummy.csv"))

builder = PromptBuilder(tool_registry=tool_registry)

prompt = builder.build(context)

print("\n========== PROMPT ==========\n")

print(prompt)