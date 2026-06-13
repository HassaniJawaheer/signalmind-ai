class ToolOutputFormatter:

    def format(self,tool_output) -> str:

        text = ""

        for key, value in tool_output.items():

            text += f"{key}\n"

            if isinstance(value,dict):

                for sub_key, sub_value in value.items():

                    text += f"{sub_key}: {sub_value}\n"

            elif isinstance(value, list):

                values = ", ".join(
                    str(x)
                    for x in value
                )

                text += f"{values}\n"

            else:

                text += f"{value}\n"

            text += "\n"

        return text