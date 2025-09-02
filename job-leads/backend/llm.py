from __future__ import annotations

import os
from typing import Dict, List

import httpx


class LLMProvider:
    async def suggest(self, kind: str, prompt: str) -> str:
        raise NotImplementedError


class OllamaProvider(LLMProvider):
    def __init__(self, base: str | None = None, model: str | None = None) -> None:
        self.base = base or os.getenv("OLLAMA_BASE", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3:8b")

    async def suggest(self, kind: str, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{self.base}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a concise, helpful career assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                },
            )
            r.raise_for_status()
            data = r.json()
            # Ollama returns {message: {content: ...}}
            return data.get("message", {}).get("content", "")


class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def suggest(self, kind: str, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": "openrouter/auto",
                    "messages": [
                        {"role": "system", "content": "You are a concise, helpful career assistant."},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            r.raise_for_status()
            data = r.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""


def get_default_provider() -> LLMProvider:
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        return OpenRouterProvider(key)
    return OllamaProvider()

