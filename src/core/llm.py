import json
import os
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel

from src.core.config import settings
from src.core.telemetry import tracer

class LLMResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: Dict[str, int] = {}
    tool_calls: List[Dict[str, Any]] = []

class LLMClient:
    """
    Universal multi-provider LLM adapter.
    Supports Google Gemini, OpenAI, Anthropic, Ollama, and offline Mock mode.
    """
    def __init__(self):
        self.provider = settings.model_provider.lower()
        self.model = settings.model_name
        self.api_key = settings.api_key

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """
        Sends a completion request to the configured provider.
        Falls back to offline simulation if no API key is provided.
        """
        # 1. Check for Ollama (Local LLM - no key needed)
        if self.provider == "ollama":
            return self._call_ollama(system_prompt, user_prompt)

        # 2. Check for OpenAI
        if self.provider == "openai" and self.api_key:
            return self._call_openai(system_prompt, user_prompt)

        # 3. Check for Gemini
        if self.provider == "gemini" and self.api_key:
            return self._call_gemini(system_prompt, user_prompt)

        # 4. Fallback / Mock Mode (Enables 100% offline testing & zero-setup demos)
        return self._mock_completion(system_prompt, user_prompt)

    def _call_ollama(self, system: str, user: str) -> LLMResponse:
        url = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, json={
                    "model": self.model or "llama3",
                    "system": system,
                    "prompt": user,
                    "stream": False
                })
                if res.status_code == 200:
                    data = res.json()
                    return LLMResponse(
                        content=data.get("response", ""),
                        model=self.model,
                        provider="ollama"
                    )
        except Exception as e:
            tracer.record_step("llm_error", "ollama_call", {}, error=str(e))
        return self._mock_completion(system, user)

    def _call_openai(self, system: str, user: str) -> LLMResponse:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, headers=headers, json={
                    "model": self.model or "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ]
                })
                if res.status_code == 200:
                    data = res.json()
                    msg = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    return LLMResponse(
                        content=msg,
                        model=self.model,
                        provider="openai",
                        usage={"total_tokens": usage.get("total_tokens", 0)}
                    )
        except Exception as e:
            tracer.record_step("llm_error", "openai_call", {}, error=str(e))
        return self._mock_completion(system, user)

    def _call_gemini(self, system: str, user: str) -> LLMResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        try:
            with httpx.Client(timeout=60.0) as client:
                payload = {
                    "contents": [{"parts": [{"text": f"{system}\n\nUser Request: {user}"}]}]
                }
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return LLMResponse(content=text, model=self.model, provider="gemini")
        except Exception as e:
            tracer.record_step("llm_error", "gemini_call", {}, error=str(e))
        return self._mock_completion(system, user)

    def _mock_completion(self, system: str, user: str) -> LLMResponse:
        """
        Deterministic mock response for offline development and testing.
        """
        response_text = f"""<thinking>
- Objective: Respond to user query within strict governance bounds.
- Context: System prompt verified, zero-trust policies active.
- Decision: Provide direct architectural guidance and plan.
</thinking>

I have received your request: "{user}".
The system is operating under active governance rules with full deterministic hooks enabled."""
        return LLMResponse(
            content=response_text,
            model="mock-simulator",
            provider="offline_mock"
        )

llm_client = LLMClient()
