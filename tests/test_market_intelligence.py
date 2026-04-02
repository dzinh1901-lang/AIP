"""Tests for MarketIntelligenceAgent (Agent 3)."""

from __future__ import annotations

import pytest

from aip.agents.market_intelligence import MarketIntelligenceAgent
from aip.core.message_bus import AgentMessage


class TestMarketIntelligenceAgent:
    def _make_agent(self, context, bus, sched, mock_llm):
        return MarketIntelligenceAgent(context, bus=bus, sched=sched)

    def test_agent_name(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        assert agent.AGENT_NAME == "market_intelligence"

    def test_analyse_asset_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.analyse_asset("BTC", "price=65000, change_24h=+2.5%")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_answer_market_query_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.answer_market_query("Is gold in an uptrend?")
        assert isinstance(result, str)

    def test_generate_signal_report_returns_string(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent.generate_signal_report(["BTC", "ETH", "Gold"])
        assert isinstance(result, str)

    def test_scan_skips_empty_snapshots(self, context, bus, sched, mock_llm):
        context.market_snapshots = []
        agent = self._make_agent(context, bus, sched, mock_llm)
        agent._scan_and_alert()
        mock_llm.assert_not_called()

    def test_scan_broadcasts_when_signal_found(self, context, bus, sched, mock_llm):
        mock_llm.return_value = "BTC: Bullish, confidence 80%, strong volume surge."
        agent = self._make_agent(context, bus, sched, mock_llm)
        received = []
        bus.subscribe("broadcast", lambda m: received.append(m))
        agent._scan_and_alert()
        assert any(m.subject == "Market Alert" for m in received)

    def test_scan_no_broadcast_when_none(self, context, bus, sched, mock_llm):
        mock_llm.return_value = "NONE"
        agent = self._make_agent(context, bus, sched, mock_llm)
        received = []
        bus.subscribe("broadcast", lambda m: received.append(m))
        agent._scan_and_alert()
        assert not any(m.subject == "Market Alert" for m in received)

    def test_handle_analysis_request(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        replies = []
        bus.subscribe("orchestrator", lambda m: replies.append(m))
        msg = AgentMessage(
            sender="orchestrator",
            recipient="market_intelligence",
            subject="Analyse Asset",
            body="BTC|||price=65000",
        )
        agent.handle_message(msg)
        assert len(replies) == 1
        assert replies[0].metadata.get("type") == "asset_analysis"

    def test_handle_signal_report_request(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        replies = []
        bus.subscribe("orchestrator", lambda m: replies.append(m))
        msg = AgentMessage(
            sender="orchestrator",
            recipient="market_intelligence",
            subject="Signal Report",
            body="BTC, ETH, Gold",
        )
        agent.handle_message(msg)
        assert replies[0].metadata.get("type") == "signal_report"

    def test_format_snapshots(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        formatted = agent._format_snapshots(context.market_snapshots)
        assert "BTC" in formatted
        assert "Gold" in formatted

    def test_format_snapshots_empty(self, context, bus, sched, mock_llm):
        agent = self._make_agent(context, bus, sched, mock_llm)
        result = agent._format_snapshots([])
        assert "No data" in result
