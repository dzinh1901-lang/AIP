"""Shared test fixtures and helpers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aip.agents.base import AgentContext
from aip.core.message_bus import MessageBus
from aip.core.scheduler import AgentScheduler


@pytest.fixture()
def context() -> AgentContext:
    """Minimal AgentContext with sample data."""
    ctx = AgentContext()
    ctx.active_users = [
        {"name": "Alice", "email": "alice@example.com", "interest": "crypto", "days_since_login": 1},
        {"name": "Bob", "email": "bob@example.com", "interest": "commodities", "days_since_login": 10},
    ]
    ctx.active_leads = [
        {"name": "Carol", "email": "carol@example.com", "interest": "both", "stage": "warm"},
    ]
    ctx.market_snapshots = [
        {"asset": "BTC", "price": 65000, "change_24h": "+2.5%", "volume": "35B"},
        {"asset": "Gold", "price": 2350, "change_24h": "-0.3%", "volume": "12B"},
    ]
    return ctx


@pytest.fixture()
def bus() -> MessageBus:
    return MessageBus()


@pytest.fixture()
def sched() -> AgentScheduler:
    return AgentScheduler()


@pytest.fixture()
def mock_llm():
    """Patch the LLM client so tests never call the real OpenAI API."""
    with patch("aip.core.llm_client.llm_client.chat", return_value="Mocked LLM response") as m:
        yield m
