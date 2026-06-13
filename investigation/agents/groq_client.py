import os
import requests
from dotenv import load_dotenv

load_dotenv()


class GroqClient:

    def __init__(self):

        self.api_key = os.getenv("GROQ_API_KEY")

        self.model = os.getenv("GROQ_MODEL")

        self.url = os.getenv(
            "GROQ_API_URL",
            "https://api.groq.com/openai/v1/chat/completions"
        )

        if not self.api_key:

            raise ValueError("GROQ_API_KEY is not set.")

        self.temperature = float(os.getenv("GROQ_TEMPERATURE",0.0))

        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS",512))

    def generate(self, prompt: str) -> str:

        headers = {

            "Authorization":
                f"Bearer {self.api_key}",

            "Content-Type":
                "application/json"
        }

        payload = {

            "model":
                self.model,

            "messages": [

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            "temperature": self.temperature,

            "max_tokens": self.max_tokens
        }

        response = requests.post(
            self.url,
            headers=headers,
            json=payload
        )

        response.raise_for_status()

        content = (
            response
            .json()["choices"][0]
            ["message"]["content"]
        )

        return content