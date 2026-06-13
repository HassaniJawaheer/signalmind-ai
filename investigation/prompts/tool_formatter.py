from investigation.tools.tool_registry import ToolRegistry

class ToolFormatter:
    def format(self, registry: ToolRegistry) -> str:
        
        tools_description = registry.describe_tools()
        text = "Available tools:\n\n"

        for tool in tools_description:
            text += (
                f"Tool name: {tool['name']}\n"
                f"Description: {tool['description']}\n\n"
            )
        
        return text