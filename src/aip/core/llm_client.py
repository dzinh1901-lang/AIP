"""LLM client – thin wrapper around the OpenAI Chat Completions API."""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from aip.config import config

logger = logging.getLogger(__name__)


class LLMClient:
    """Synchronous OpenAI chat-completions client shared by all agents."""

    def __init__(self) -> None:
        self._client = OpenAI(api_key=config.OPENAI_API_KEY)

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        extra_messages: list[dict[str, Any]] | None = None,
    ) -> str:
        """Send a chat request and return the assistant reply text.

        Args:
            system_prompt: The system-role prompt defining the agent persona.
            user_message: The human-turn message.
            model: Override the default model from config.
            temperature: Override the default temperature from config.
            extra_messages: Additional messages inserted between system and user.

        Returns:
            The assistant's reply as a plain string.
        """
        messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        if extra_messages:
            messages.extend(extra_messages)
        messages.append({"role": "user", "content": user_message})

        response = self._client.chat.completions.create(
            model=model or config.LLM_MODEL,
            temperature=temperature if temperature is not None else config.LLM_TEMPERATURE,
            messages=messages,
        )
        reply = response.choices[0].message.content or ""
        logger.debug("LLM reply (%d chars)", len(reply))
        return reply


# Module-level singleton – agents import this directly.
llm_client = LLMClient()
