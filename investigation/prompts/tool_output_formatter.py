import json
from config import settings


class ToolOutputFormatter:

    def present(self, value):
        if isinstance(value, float):
            return round(value, settings.PROMPT_DECIMAL_PLACES)
        if isinstance(value, dict):
            return {key: self.present(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.present(item) for item in value]
        return value

    def format(self, tool_output) -> str:
        return json.dumps(self.present(tool_output), ensure_ascii=False, allow_nan=False)
