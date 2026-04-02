"""Tests for OrchestratorAgent (Agent 1)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from aip.agents.orchestrator import OrchestratorAgent
from aip.core.message_bus import AgentMessage


class TestOrchestratorAgent:
    def _make_agent(self, context, bus, sched, mock_llm):
        return OrchestratorAgent(context, bus=bus, sched=sched)

    def test_agent_name(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        assert agent.AGENT_NAME == "orchestrator"

    def test_register_jobs_does_not_raise(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        agent.register_jobs()  # should not raise

    def test_admin_query_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.admin_query("What is our current user count?")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_daily_briefing_broadcasts(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        received = []
        bus.subscribe("broadcast", lambda m: received.append(m))
        agent._daily_briefing()
        assert any(m.subject == "Daily Operational Briefing" for m in received)

    def test_status_reports_cleared_after_briefing(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        agent._status_reports = [{"agent": "marketing", "body": "ok", "subject": "Status Update"}]
        agent._daily_briefing()
        assert agent._status_reports == []

    def test_handle_status_update_message(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        msg = AgentMessage(
            sender="marketing",
            recipient="orchestrator",
            subject="Status Update",
            body="All good.",
        )
        agent.handle_message(msg)
        assert len(agent._status_reports) == 1
        assert agent._status_reports[0]["agent"] == "marketing"

    def test_handle_escalation_sends_reply(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        replies = []
        bus.subscribe("marketing", lambda m: replies.append(m))
        msg = AgentMessage(
            sender="marketing",
            recipient="orchestrator",
            subject="Escalation: campaign rejected",
            body="The campaign was rejected by the ad platform.",
        )
        agent.handle_message(msg)
        assert len(replies) == 1
        assert replies[0].metadata.get("type") == "escalation_response"

    def test_route_request_sends_to_valid_agent(self, context, bus, sched, mock_llm):
        mock_llm.return_value = "market_intelligence"
        agent = self._make_agent(context, bus, sched, mock_llm)
        received = []
        bus.subscribe("market_intelligence", lambda m: received.append(m))
        msg = AgentMessage(
            sender="admin",
            recipient="orchestrator",
            subject="Route Request",
            body="Analyse BTC for me.",
        )
        agent.handle_message(msg)
        assert len(received) == 1

    def test_collect_agent_status_sends_four_messages(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        sent = []
        for name in ("marketing", "market_intelligence", "customer_success", "analytics"):
            bus.subscribe(name, lambda m, _n=name: sent.append(m))
        agent._collect_agent_status()
        assert len(sent) == 4

    def test_ignores_own_broadcast(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        initial_reports = list(agent._status_reports)
        msg = AgentMessage(
            sender="orchestrator",
            recipient="broadcast",
            subject="Daily Operational Briefing",
            body="...",
        )
        agent.handle_message(msg)
        assert agent._status_reports == initial_reports
