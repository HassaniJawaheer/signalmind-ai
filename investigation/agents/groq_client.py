import os
import json
import requests
from math import isfinite
from time import monotonic, sleep
from config import settings
from investigation.errors import InvestigationError
from dotenv import load_dotenv

load_dotenv()


class GroqClient:

    def __init__(self, connect_timeout: float = 5.0, read_timeout: float = 30.0):

        for timeout in (connect_timeout, read_timeout):
            if not isfinite(timeout) or timeout <= 0:
                raise ValueError("HTTP timeouts must be finite and positive.")
        self.timeout = (connect_timeout, read_timeout)
        self.min_call_interval = settings.GROQ_MIN_CALL_INTERVAL_SECONDS
        if not isfinite(self.min_call_interval) or self.min_call_interval < 0:
            raise ValueError("GROQ_MIN_CALL_INTERVAL_SECONDS must be finite and non-negative.")
        self.last_call_started_at = None

        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL")
        self.url = os.getenv(
            "GROQ_API_URL",
            "https://api.groq.com/openai/v1/chat/completions"
        )

        if not self.api_key:

            raise ValueError("GROQ_API_KEY is not set.")

        self.temperature = float(os.getenv("GROQ_TEMPERATURE",0.0))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", 512))

    def generate(self, prompt: str) -> str:

        headers = {

            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [

                {
                    "role": "user",
                    "content": prompt
                }

            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        self.wait_before_call()
        self.last_call_started_at = monotonic()

        try:
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
        except requests.Timeout as error:
            raise InvestigationError("api_timeout", "The API request timed out.") from error
        except requests.ConnectionError as error:
            raise InvestigationError("network_error", "Unable to connect to the API.") from error
        except requests.RequestException as error:
            raise InvestigationError("api_error", "The API request failed.") from error

        if not response.ok:
            self.print_api_error(response)
            self.raise_api_error(response)

        try:
            content = response.json()["choices"][0]["message"]["content"]
            if not isinstance(content, str) or not content.strip():
                raise ValueError("Missing response content.")
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise InvestigationError("invalid_response", "The API returned an invalid response.") from error

        return content

    def wait_before_call(self) -> None:
        if self.last_call_started_at is None:
            return
        elapsed = monotonic() - self.last_call_started_at
        remaining = self.min_call_interval - elapsed
        if remaining > 0:
            print(f"Waiting {remaining:.1f} seconds before the next Groq request.")
            sleep(remaining)

    def print_api_error(self, response) -> None:
        # Temporary diagnostic; omit request headers and redact the API key.
        try:
            body = response.json()
            if isinstance(body, dict):
                body = body.get("error", body)
            details = json.dumps(body, ensure_ascii=False)
        except ValueError:
            details = response.text

        diagnostic = (
            f"Groq HTTP error: {response.status_code}\n"
            f"Requested model: {self.model}\n"
            f"Response: {details}"
        )
        if self.api_key:
            diagnostic = diagnostic.replace(self.api_key, "[REDACTED]")
        print(diagnostic[:2000])

    def raise_api_error(self, response) -> None:
        # Never expose the raw response, request headers, or exception text.
        code = None
        try:
            details = response.json().get("error", {})
            if isinstance(details, dict):
                code = details.get("code")
        except (ValueError, AttributeError):
            pass

        if code in ("context_length_exceeded", "context_window_exceeded"):
            raise InvestigationError("context_limit", "The API reported that the context limit was exceeded.")
        if code in ("insufficient_quota", "quota_exceeded"):
            raise InvestigationError("quota_exceeded", "The API reported an exhausted quota.")
        if response.status_code == 429:
            raise InvestigationError("rate_limit", "The API rejected the request due to a usage limit.")
        if response.status_code in (401, 403):
            raise InvestigationError("authentication_error", "The API denied access to the request.")
        raise InvestigationError("api_error", f"The API returned HTTP {response.status_code}.")
