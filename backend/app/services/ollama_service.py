import requests

from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL


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

        response = requests.post(
            url,
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            raise ValueError(
                "Ollama response does not contain the expected 'response' field."
            )

        return data["response"]


ollama_service = OllamaService()