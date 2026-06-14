from investigation.agents.groq_client import GroqClient
from investigation.agents.output_parser import OutputParser
from investigation.models.agent_action import AgentAction
from investigation.models.context import Context
from investigation.agents.prompt_builder import PromptBuilder
from investigation.agents.cleaner import Cleaner
from investigation.tools.tool_registry import ToolRegistry


class LLMAgent:

    def __init__(self, tool_registry: ToolRegistry):
        self.prompt_builder = PromptBuilder(tool_registry=tool_registry)
        self.client = GroqClient()
        self.parser = OutputParser()
        self.cleaner = Cleaner()

    def decide(self, context: Context) -> AgentAction:
        prompt = self.prompt_builder.build(context)
        print(len(prompt))
        output = self.client.generate(prompt)
        clean_output = self.cleaner.clean(output)
        
        print("\n========== LLM OUTPUT ==========\n")
        print(clean_output)
        
        action = self.parser.parse(clean_output)

        return action