"""Base agent class shared by all AIP platform agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from aip.core.llm_client import llm_client
from aip.core.message_bus import AgentMessage, MessageBus, message_bus
from aip.core.scheduler import AgentScheduler, scheduler

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Shared mutable context available to every agent."""

    platform_name: str = "AIP"
    active_users: list[dict[str, Any]] = field(default_factory=list)
    active_leads: list[dict[str, Any]] = field(default_factory=list)
    market_snapshots: list[dict[str, Any]] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseAgent(ABC):
    """Abstract base for all AIP platform agents.

    Subclasses must implement:
    - ``AGENT_NAME``     – unique string identifier.
    - ``SYSTEM_PROMPT``  – persona/role description injected into every LLM call.
    - ``register_jobs``  – declare recurring scheduled tasks.
    - ``handle_message`` – react to inbound ``AgentMessage`` objects.
    """

    AGENT_NAME: str = "base"
    SYSTEM_PROMPT: str = "You are an AI assistant."

    def __init__(
        self,
        context: AgentContext,
        bus: MessageBus | None = None,
        sched: AgentScheduler | None = None,
    ) -> None:
        self.context = context
        self.bus = bus or message_bus
        self.scheduler = sched or scheduler
        self._log = logging.getLogger(f"aip.agent.{self.AGENT_NAME}")
        self.bus.subscribe(self.AGENT_NAME, self.handle_message)
        self.bus.subscribe("broadcast", self.handle_message)

    # ------------------------------------------------------------------
    # LLM helpers
    # ------------------------------------------------------------------

    def think(self, prompt: str, **kwargs: Any) -> str:
        """Send *prompt* to the LLM under this agent's persona and return the reply."""
        return llm_client.chat(self.SYSTEM_PROMPT, prompt, **kwargs)

    # ------------------------------------------------------------------
    # Messaging helpers
    # ------------------------------------------------------------------

    def send(self, recipient: str, subject: str, body: str, **metadata: Any) -> None:
        """Publish a message to *recipient* on the shared bus."""
        msg = AgentMessage(
            sender=self.AGENT_NAME,
            recipient=recipient,
            subject=subject,
            body=body,
            metadata=metadata,
        )
        self.bus.publish(msg)

    def broadcast(self, subject: str, body: str, **metadata: Any) -> None:
        """Broadcast a message to all subscribed agents."""
        self.send("broadcast", subject, body, **metadata)

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def register_jobs(self) -> None:
        """Register recurring scheduled jobs for this agent."""

    @abstractmethod
    def handle_message(self, message: AgentMessage) -> None:
        """React to an inbound AgentMessage."""

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Register jobs and log startup."""
        self.register_jobs()
        self._log.info("%s agent started", self.AGENT_NAME)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.AGENT_NAME!r}>"
