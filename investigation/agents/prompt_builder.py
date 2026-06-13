from investigation.prompts.context_formatter import ContextFormatter
from investigation.prompts.output_schema import OUTPUT_SCHEMA
from investigation.prompts.system_prompt import SYSTEM_PROMPT
from investigation.prompts.tool_formatter import ToolFormatter
from investigation.tools.tool_registry import ToolRegistry

class PromptBuilder:
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.context_formatter = ContextFormatter()
        self.tool_formatter = ToolFormatter()

    def build(self, context: ContextFormatter) -> str:
        prompt = ""

        prompt += SYSTEM_PROMPT

        prompt += "\n\n"

        prompt += self.context_formatter.format(context)

        prompt += "\n\n"

        prompt += self.tool_formatter.format(self.tool_registry)

        prompt += "\n\n"

        prompt += OUTPUT_SCHEMA

        return prompt