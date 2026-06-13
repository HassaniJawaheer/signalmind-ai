from investigation.models.context import Context
from investigation.prompts.tool_output_formatter import ToolOutputFormatter


class ContextFormatter:
    def __init__(self):
        self.tool_output_formatter = ToolOutputFormatter()

    def format(self,context: Context) -> str:

        text = ""

        text += (
            "Initial anomaly\n\n"
            "The following sensor values triggered the investigation.\n"
            "These values remain constant during the investigation.\n\n"
            f"Timestamp:\n"
            f"{context.request.timestamp}\n\n"
            "Sensor values:\n"
        )

        for sensor, value in context.request.sensor_values.items():

            text += f"{sensor}: {value}\n"

        text += "\n"

        text += "Investigation history\n\n"

        text += "Previous observations:\n"

        if context.observations:

            for i, observation in enumerate(context.observations, start=1):
                text += f"{i}. {observation}\n"

        else:

            text += "No observations yet.\n"

        text += "\n"

        text += "Previous hypotheses:\n"

        if context.hypotheses:
            for i, hypothesis in enumerate(context.hypotheses,start=1):
                text += f"{i}. {hypothesis}\n"
        else:

            text += "No hypotheses yet.\n"

        text += "\n"

        text += "Previous tool calls:\n"

        if context.tool_calls:

            for tool_call in context.tool_calls:

                text += (
                    f"\nTool name: {tool_call.tool_name}\n"
                    "Tool input:\n"
                )

                for key, value in tool_call.tool_input.items():

                    text += f"{key}: {value}\n"

                tool_output = self.tool_output_formatter.format(tool_call.tool_output)

                text += (
                    "\nTool output:\n"
                    f"{tool_output}\n"
                )
        else:

            text += "No tool calls yet.\n"

        return text