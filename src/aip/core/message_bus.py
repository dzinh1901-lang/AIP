"""In-process message bus for inter-agent communication.

Agents publish typed ``AgentMessage`` objects; any number of subscribers
can listen for messages addressed to them (or broadcast to all).
"""

from __future__ import annotations

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """A message exchanged between agents or between an agent and the platform."""

    sender: str
    recipient: str  # agent name or "broadcast"
    subject: str
    body: str
    metadata: dict = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return (
            f"AgentMessage(id={self.message_id[:8]}, "
            f"from={self.sender}, to={self.recipient}, subject={self.subject!r})"
        )


Handler = Callable[[AgentMessage], None]


class MessageBus:
    """Thread-safe publish/subscribe message bus.

    Usage::

        bus = MessageBus()
        bus.subscribe("orchestrator", my_handler)
        bus.publish(AgentMessage(sender="marketing", recipient="orchestrator", ...))
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # recipient name → list of handlers
        self._subscribers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, recipient: str, handler: Handler) -> None:
        """Register *handler* to receive messages addressed to *recipient*."""
        with self._lock:
            self._subscribers[recipient].append(handler)
        logger.debug("Subscribed handler for recipient=%s", recipient)

    def publish(self, message: AgentMessage) -> None:
        """Deliver *message* to all matching subscribers (synchronously).

        Messages with ``recipient="broadcast"`` are delivered to every
        registered subscriber.
        """
        with self._lock:
            if message.recipient == "broadcast":
                handlers = [h for handlers in self._subscribers.values() for h in handlers]
            else:
                handlers = list(self._subscribers.get(message.recipient, []))

        if not handlers:
            logger.warning("No subscribers for recipient=%s", message.recipient)
            return

        logger.info("Publishing %r", message)
        for handler in handlers:
            try:
                handler(message)
            except Exception:
                logger.exception("Handler error for %r", message)


# Module-level singleton shared by all agents and the platform layer.
message_bus = MessageBus()
