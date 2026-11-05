def main():
    from data.measurement_history import MeasurementHistory
    from investigation.models.context import Context
    from investigation.models.request import Request
    from investigation.models.tool_call import ToolCall
    from investigation.agents.prompt_builder import PromptBuilder
    from investigation.tools.tool_registry import ToolRegistry
    from investigation.tools.history_tool import HistoryTool
    from investigation.tools.statistics_tool import StatisticsTool


    request = Request(
        timestamp="2026-06-13T15:00:00+00:00",
        sensor_values={
            "temperature": 119.8,
            "rotational_speed": 2900.0,
            "pressure": 1.96,
            "flow_rate": 12.0
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
                turn=1,
                tool_input={
                    "sensors": ["temperature"],
                    "timestamp": request.timestamp,
                    "n_points": 10
                },
                tool_output={
                    "temperature": [95.2, 101.3, 108.4, 119.8]
                }
            ),
            ToolCall(
                tool_name="statistics",
                turn=2,
                tool_input={
                    "timestamp": request.timestamp,
                    "n_points": 10
                },
                tool_output={
                    "temperature": {
                        "mean": 106.2,
                        "std": 8.7,
                        "delta": 24.6
                    }
                }
            )
        ]
    )

    context.observation_turns = [1, 2]
    context.hypothesis_turns = [2]
    context.iterations = 3

    tool_registry = ToolRegistry()
    history = MeasurementHistory("dummy.jsonl")

    tool_registry.register(HistoryTool(history=history))

    tool_registry.register(StatisticsTool(history=history))

    builder = PromptBuilder(tool_registry=tool_registry)

    prompt = builder.build(context)

    print("\n========== PROMPT ==========\n")

    print(prompt)


if __name__ == "__main__":
    main()
