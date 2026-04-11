#!/usr/bin/env python3
"""
Conversation Engine — Ollama Chat Client
==========================================
Async client wrapping Ollama's /api/chat endpoint.
Supports:
- Tool calling (function invocation)
- Structured output (JSON schema via format parameter)
- Thinking control (/think, /no_think)
- All sampling parameters per request
- Retry with exponential backoff

This is separate from orchestrator/src/models/ollama_client.py which
uses /api/generate. This client uses /api/chat exclusively.

LOG-0018: Foundation deploy.
"""
import json
import logging
import os
from typing import Any, Optional

import aiohttp

from .models import ConversationConfig

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_CHAT_TIMEOUT", "120"))


class OllamaChatClient:
    """Async client for Ollama /api/chat with full conversation control.

    Usage::

        async with OllamaChatClient() as client:
            response = await client.chat(config, messages)
            print(response["message"]["content"])

    Or without context manager::

        client = OllamaChatClient()
        await client.connect()
        response = await client.chat(config, messages)
        await client.close()
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int | None = None,
        max_retries: int = 3,
    ):
        self.base_url = (base_url or OLLAMA_HOST).rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout or OLLAMA_TIMEOUT)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "OllamaChatClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    async def connect(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def chat(
        self,
        config: ConversationConfig,
        messages: list[dict],
    ) -> dict:
        """Send a chat request to Ollama.

        Args:
            config: Full ConversationConfig with all levers set.
            messages: The messages array (system + history + current).

        Returns:
            Raw Ollama response dict with at minimum:
            - message.content: The response text
            - message.tool_calls: Any tool invocations (if tools provided)
            - prompt_eval_count, eval_count: Token counts
        """
        payload = config.to_ollama_payload(messages)
        return await self._request(payload)

    async def chat_raw(self, payload: dict) -> dict:
        """Send a raw payload to /api/chat. For advanced use cases."""
        return await self._request(payload)

    async def _request(self, payload: dict) -> dict:
        """Make HTTP request with retry logic."""
        import asyncio

        if self.session is None:
            await self.connect()

        url = f"{self.base_url}/api/chat"

        for attempt in range(self.max_retries):
            try:
                async with self.session.request("POST", url, json=payload) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        error_text = await resp.text()
                        logger.warning(
                            f"Ollama chat failed (attempt {attempt + 1}/{self.max_retries}): "
                            f"{resp.status} — {error_text[:200]}"
                        )
                        if attempt == self.max_retries - 1:
                            raise RuntimeError(
                                f"Ollama chat API error: {resp.status} — {error_text[:500]}"
                            )
                        await asyncio.sleep(2**attempt)

            except aiohttp.ClientError as e:
                logger.warning(
                    f"Ollama connection error (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Failed to connect to Ollama: {e}") from e
                await asyncio.sleep(2**attempt)

        # Should never reach here
        raise RuntimeError("Ollama chat: exhausted retries")

    async def health_check(self) -> bool:
        """Check if Ollama is responsive."""
        import asyncio

        if self.session is None:
            await self.connect()

        try:
            async with self.session.request(
                "GET", f"{self.base_url}/api/tags"
            ) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
