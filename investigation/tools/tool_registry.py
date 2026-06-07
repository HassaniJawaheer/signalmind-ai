from investigation.tools.base_tool import BaseTool


class ToolRegistry:

    def __init__(self):
        self._tools = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> BaseTool:
        if tool_name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self._tools[tool_name]

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def describe_tools(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self._tools.values()
        ]