from config import settings
from investigation.models.context import Context
from investigation.prompts.tool_output_formatter import ToolOutputFormatter


class ContextFormatter:
    def __init__(self):
        self.tool_output_formatter = ToolOutputFormatter()

    def format(self, context: Context) -> str:
        window = settings.PROMPT_RECENT_TURNS
        if isinstance(window, bool) or not isinstance(window, int) or window <= 0:
            raise ValueError("PROMPT_RECENT_TURNS must be a positive integer.")
        if len(context.observations) != len(context.observation_turns):
            raise ValueError("Each observation must have a turn number.")
        if len(context.hypotheses) != len(context.hypothesis_turns):
            raise ValueError("Each hypothesis must have a turn number.")

        # decide() increments iterations before building this prompt.
        last_turn = max(context.observation_turns + context.hypothesis_turns
                        + [call.turn for call in context.tool_calls] + [0])
        completed_turn = max(last_turn, context.iterations - 1)
        first_turn = max(1, completed_turn - window + 1)
        formatter = self.tool_output_formatter
        text = ""
        if context.max_decisions is not None:
            decision = max(1, context.iterations)
            remaining = max(0, context.max_decisions - decision)
            text += (
                f"Decision {decision} of {context.max_decisions}. "
                f"{remaining} decisions remaining after this one.\n"
            )
            if remaining == 0:
                text += (
                    "This is your last decision: return finish with a cautious synthesis "
                    "of available evidence and uncertainties, rather than another tool call.\n"
                )
            text += "\n"
        text += (
            "Initial anomaly (fixed reference):\n"
            f"Timestamp: {context.request.timestamp}\n"
            f"Sensor values: {formatter.format(context.request.sensor_values)}\n\n"
            f"Recent investigation turns: {first_turn} to {completed_turn}. "
            "Older turns are omitted from this prompt, not deleted.\n"
            "Observations reported by the agent:\n"
        )
        for turn, observation in zip(context.observation_turns, context.observations):
            if first_turn <= turn <= completed_turn:
                text += f"Turn {turn}: {observation}\n"
        text += "\nHypotheses (not established facts):\n"
        for turn, hypothesis in zip(context.hypothesis_turns, context.hypotheses):
            if first_turn <= turn <= completed_turn:
                text += f"Turn {turn}: {hypothesis}\n"
        text += "\nTool evidence:\n"
        for call in context.tool_calls:
            if first_turn <= call.turn <= completed_turn:
                text += (
                    f"Turn {call.turn}, tool: {call.tool_name}\n"
                    f"Input: {formatter.format(call.tool_input)}\n"
                    f"Output: {formatter.format(call.tool_output)}\n"
                )
        return text
