from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, List, Dict, Any, Optional
import httpx
from loguru import logger
from app.config import get_settings

class OllamaClient:
    """Async HTTP client for Ollama LLM server with streaming and retry logic."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url: str = self.settings.OLLAMA_BASE_URL.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.settings.OLLAMA_TIMEOUT, connect=10.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """
        Stream chat completion token-by-token with exponential backoff on connection errors.
        """
        model_name = model or self.settings.OLLAMA_MODEL
        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        max_retries = 3
        backoff_delay = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                client = await self.get_client()
                async with client.stream("POST", "/api/chat", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token

                        if chunk.get("done", False):
                            eval_count = chunk.get("eval_count", 0)
                            logger.debug("Ollama streaming completed. Tokens generated: {}", eval_count)
                            return
                return
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.NetworkError) as err:
                logger.warning("Ollama connection attempt {}/{} failed: {}", attempt, max_retries, err)
                if attempt == max_retries:
                    raise RuntimeError(f"Failed to communicate with Ollama at {self.base_url}: {err}") from err
                await asyncio.sleep(backoff_delay)
                backoff_delay *= 2
            except httpx.HTTPStatusError as err:
                logger.error("Ollama HTTP status error: {}", err)
                raise RuntimeError(f"Ollama returned error: {err.response.text}") from err

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Non-streaming chat completion."""
        tokens: List[str] = []
        async for token in self.stream_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            tokens.append(token)
        return "".join(tokens)

    async def list_models(self) -> List[str]:
        """Fetch list of local models installed in Ollama."""
        try:
            client = await self.get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
        except Exception as err:
            logger.error("Failed to query Ollama models: {}", err)
            return []

    async def check_health(self) -> bool:
        """Verify Ollama server accessibility."""
        try:
            client = await self.get_client()
            response = await client.get("/")
            return response.status_code == 200
        except Exception:
            return False

ollama_client = OllamaClient()
