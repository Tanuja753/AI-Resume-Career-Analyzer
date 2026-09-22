import requests

from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL


class OllamaUnavailableError(Exception):
    """Raised when the Ollama server cannot be reached."""


class OllamaService:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url.rstrip('/')}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=300,
            )

        except requests.exceptions.ConnectionError as exc:
            raise OllamaUnavailableError(
                "Ollama is not available. "
                "Interview question generation requires "
                "a running Ollama server."
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise OllamaUnavailableError(
                "Ollama request timed out. "
                "Please make sure the Ollama server is running."
            ) from exc

        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            raise ValueError(
                "Ollama response does not contain the expected "
                "'response' field."
            )

        return data["response"]


ollama_service = OllamaService()