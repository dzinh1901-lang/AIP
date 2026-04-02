"""Tests for MarketingAgent (Agent 2)."""

from __future__ import annotations

import pytest

from aip.agents.marketing import MarketingAgent
from aip.core.message_bus import AgentMessage


class TestMarketingAgent:
    def _make_agent(self, context, bus, sched, mock_llm):
        return MarketingAgent(context, bus=bus, sched=sched)

    def test_agent_name(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        assert agent.AGENT_NAME == "marketing"

    def test_generate_outreach_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        lead = {"name": "Carol", "email": "carol@example.com", "interest": "crypto", "stage": "warm"}
        result = agent.generate_outreach(lead)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_create_campaign_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.create_campaign("Target crypto day traders in Q3.")
        assert isinstance(result, str)

    def test_qualify_lead_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.qualify_lead("Signed up via blog post, visited pricing page 3 times.")
        assert isinstance(result, str)

    def test_generate_social_post_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.generate_social_post("BTC just hit a new 90-day high.")
        assert isinstance(result, str)

    def test_user_referral_message_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.user_referral_message("Alice", "real-time crypto signals")
        assert isinstance(result, str)

    def test_handle_status_request(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        orchestrator_msgs = []
        bus.subscribe("orchestrator", lambda m: orchestrator_msgs.append(m))
        msg = AgentMessage(
            sender="orchestrator",
            recipient="marketing",
            subject="Status Request",
            body="",
        )
        agent.handle_message(msg)
        assert len(orchestrator_msgs) == 1
        assert orchestrator_msgs[0].subject == "Status Update"

    def test_handle_campaign_request(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        replies = []
        bus.subscribe("orchestrator", lambda m: replies.append(m))
        msg = AgentMessage(
            sender="orchestrator",
            recipient="marketing",
            subject="Campaign Request",
            body="Launch Q4 crypto campaign.",
        )
        agent.handle_message(msg)
        assert len(replies) == 1
        assert replies[0].metadata.get("type") == "campaign_plan"

    def test_handle_lead_qualification(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        replies = []
        bus.subscribe("orchestrator", lambda m: replies.append(m))
        msg = AgentMessage(
            sender="orchestrator",
            recipient="marketing",
            subject="Lead Qualification",
            body="User from LinkedIn, visited pricing page.",
        )
        agent.handle_message(msg)
        assert replies[0].metadata.get("type") == "lead_qualification"

    def test_lead_gen_cycle_skips_empty_leads(self, context, bus, sched, mock_llm):
        context.active_leads = []
        agent = self._make_agent(context, bus, sched, mock_llm)
        agent._lead_gen_cycle()  # should not raise
        mock_llm.assert_not_called()
