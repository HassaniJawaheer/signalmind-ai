OUTPUT_SCHEMA = """
Return only a valid JSON object following this example::

{
    "action_type": "call_tool",
    "tool_name": "statistics",
    "tool_input": {
        "timestamp": "...",
        "n_points": 10
    },
    "observations": "Temperature is increasing.",
    "hypotheses": "Cooling efficiency degradation suspected.",
    "final_conclusion": null
}
"""