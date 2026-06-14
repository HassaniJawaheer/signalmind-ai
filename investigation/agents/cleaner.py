import re

class Cleaner:

    def clean(self,output: str) -> str:

        # Remove <think>...</think>
        output = re.sub(
            r"<think>.*?</think>",
            "",
            output,
            flags=re.DOTALL
        )

        # Remove markdown code fences
        output = output.replace("```json","")

        output = output.replace("```","")

        # Remove leading and trailing spaces
        output = output.strip()

        # Extract JSON object
        start = output.find("{")

        end = output.rfind("}")

        if start == -1 or end == -1:

            raise ValueError("No JSON object found in LLM output.")

        output = output[start:end + 1]

        return output