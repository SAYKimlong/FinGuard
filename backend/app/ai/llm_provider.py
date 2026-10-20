"""LLM Provider - abstract interface with Ollama implementation."""

from abc import ABC, abstractmethod
from typing import Optional
import httpx
import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a text response."""
        ...

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        temperature: float = 0.3,
    ) -> dict:
        """Generate a structured (JSON) response matching a schema."""
        ...


class OllamaProvider(LLMProvider):
    """Ollama-based LLM provider."""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: float = 120.0,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.LLM_MODEL
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate text using Ollama API."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except httpx.TimeoutException:
                logger.error("Ollama request timed out")
                raise RuntimeError("LLM request timed out")
            except httpx.HTTPStatusError as e:
                logger.error(f"Ollama HTTP error: {e.response.status_code}")
                raise RuntimeError(f"LLM service error: {e.response.status_code}")
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                raise RuntimeError(f"LLM service unavailable: {e}")

    async def generate_structured(
        self,
        prompt: str,
        schema: dict,
        system_prompt: str = "",
        temperature: float = 0.3,
    ) -> dict:
        """Generate structured JSON output."""
        structured_prompt = f"""{prompt}

IMPORTANT: Respond ONLY with valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Do not include any text before or after the JSON. Return ONLY the JSON object."""

        response_text = await self.generate(
            prompt=structured_prompt,
            system_prompt=system_prompt + "\nAlways respond with valid JSON only.",
            temperature=temperature,
        )

        # Try to extract JSON from response
        try:
            # Try direct parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(response_text[start:end])
                except json.JSONDecodeError:
                    pass

            # Try array
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(response_text[start:end])
                except json.JSONDecodeError:
                    pass

            logger.warning(f"Failed to parse LLM JSON response: {response_text[:200]}")
            raise ValueError("LLM produced invalid JSON output")


class MockLLMProvider(LLMProvider):
    """Mock provider for testing when no LLM is available."""

    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 2048) -> str:
        return "This is a mock response. The AI model is not currently available. Please configure Ollama with a supported model."

    async def generate_structured(self, prompt: str, schema: dict, system_prompt: str = "", temperature: float = 0.3) -> dict:
        return {"note": "Mock response - LLM not available"}


_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """Get the configured LLM provider singleton."""
    global _provider
    if _provider is None:
        try:
            _provider = OllamaProvider()
        except Exception:
            logger.warning("Failed to initialize Ollama provider, using mock")
            _provider = MockLLMProvider()
    return _provider
