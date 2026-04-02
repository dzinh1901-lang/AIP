"""Platform integration layer – admin and user interaction interfaces.

This module wires all five agents together and exposes:
- ``AdminInterface``  – for platform administrators.
- ``UserInterface``   – for end-users of the AIP platform.
- ``Platform``        – top-level façade that bootstraps everything.
"""

from __future__ import annotations

import logging
from typing import Any

from aip.agents.analytics import AnalyticsAgent
from aip.agents.base import AgentContext
from aip.agents.customer_success import CustomerSuccessAgent
from aip.agents.market_intelligence import MarketIntelligenceAgent
from aip.agents.marketing import MarketingAgent
from aip.agents.orchestrator import OrchestratorAgent
from aip.config import config
from aip.core.message_bus import AgentMessage, message_bus
from aip.core.scheduler import scheduler

logger = logging.getLogger(__name__)


class AdminInterface:
    """Exposes platform controls and direct agent interactions to administrators."""

    def __init__(
        self,
        orchestrator: OrchestratorAgent,
        marketing: MarketingAgent,
        market_intel: MarketIntelligenceAgent,
        customer_success: CustomerSuccessAgent,
        analytics: AnalyticsAgent,
    ) -> None:
        self._orchestrator = orchestrator
        self._marketing = marketing
        self._market_intel = market_intel
        self._customer_success = customer_success
        self._analytics = analytics

    # ------------------------------------------------------------------
    # Orchestrator / COO
    # ------------------------------------------------------------------

    def ask_orchestrator(self, query: str) -> str:
        """Submit a free-text operational query to the Orchestrator agent."""
        return self._orchestrator.admin_query(query)

    def request_daily_briefing(self) -> None:
        """Trigger an on-demand daily operational briefing."""
        self._orchestrator._daily_briefing()

    # ------------------------------------------------------------------
    # Marketing
    # ------------------------------------------------------------------

    def create_campaign(self, brief: str) -> str:
        """Request a marketing campaign plan from the Marketing agent."""
        return self._marketing.create_campaign(brief)

    def qualify_lead(self, lead_info: str) -> str:
        """Ask the Marketing agent to qualify a lead."""
        return self._marketing.qualify_lead(lead_info)

    # ------------------------------------------------------------------
    # Market Intelligence
    # ------------------------------------------------------------------

    def get_signal_report(self, assets: list[str]) -> str:
        """Request a consensus signal report for specified assets."""
        return self._market_intel.generate_signal_report(assets)

    def analyse_asset(self, asset: str, data: str) -> str:
        """Request a detailed asset analysis."""
        return self._market_intel.analyse_asset(asset, data)

    def trigger_morning_briefing(self) -> None:
        """Manually trigger the morning market briefing."""
        self._market_intel._morning_briefing()

    # ------------------------------------------------------------------
    # Customer Success
    # ------------------------------------------------------------------

    def onboard_user(self, user: dict) -> str:
        """Generate an onboarding message for a new user."""
        return self._customer_success.onboard_user(user)

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_kpi_report(self) -> str:
        """Request the latest KPI report from the Analytics agent."""
        return self._analytics.generate_kpi_report()

    def get_platform_snapshot(self) -> str:
        """Request an instant platform health snapshot."""
        return self._analytics.generate_platform_snapshot()

    def ask_analytics(self, query: str) -> str:
        """Submit a free-text data query to the Analytics agent."""
        return self._analytics.admin_data_query(query)

    def detect_anomalies(self, metrics: dict) -> str:
        """Ask the Analytics agent to check a metrics dict for anomalies."""
        return self._analytics.detect_anomalies(metrics)

    # ------------------------------------------------------------------
    # Cross-agent messaging
    # ------------------------------------------------------------------

    def send_to_agent(self, agent_name: str, subject: str, body: str) -> None:
        """Send a direct message from an admin to any named agent."""
        msg = AgentMessage(
            sender="admin",
            recipient=agent_name,
            subject=subject,
            body=body,
            metadata={"source": "admin_interface"},
        )
        message_bus.publish(msg)


class UserInterface:
    """Exposes platform features and agent interactions to end-users."""

    def __init__(
        self,
        market_intel: MarketIntelligenceAgent,
        customer_success: CustomerSuccessAgent,
        marketing: MarketingAgent,
    ) -> None:
        self._market_intel = market_intel
        self._customer_success = customer_success
        self._marketing = marketing

    # ------------------------------------------------------------------
    # Market intelligence
    # ------------------------------------------------------------------

    def ask_market(self, query: str) -> str:
        """Ask a market-related question and receive an AI-powered answer."""
        return self._market_intel.user_market_query(query)

    def get_signal_report(self, assets: list[str]) -> str:
        """Request a consensus signal table for a list of assets."""
        return self._market_intel.generate_signal_report(assets)

    # ------------------------------------------------------------------
    # Support
    # ------------------------------------------------------------------

    def ask_support(self, user: dict, query: str) -> str:
        """Submit a support or platform usage question."""
        return self._customer_success.user_support_query(user, query)

    def submit_feedback(self, user: dict, feedback: str) -> str:
        """Submit product feedback and receive an acknowledgement."""
        return self._customer_success.user_feedback(user, feedback)

    # ------------------------------------------------------------------
    # Referral / marketing
    # ------------------------------------------------------------------

    def get_referral_message(self, user: dict, benefit: str) -> str:
        """Generate a referral message this user can share with contacts."""
        return self._marketing.user_referral_message(user.get("name", "User"), benefit)


class Platform:
    """Top-level façade that bootstraps all agents and exposes interfaces.

    Usage::

        platform = Platform()
        platform.start()

        # Admin interaction
        briefing = platform.admin.get_kpi_report()

        # User interaction
        answer = platform.user.ask_market("Is gold bullish today?")

        platform.stop()
    """

    def __init__(self, context: AgentContext | None = None) -> None:
        self.context = context or AgentContext(platform_name=config.PLATFORM_NAME)

        # Instantiate all five agents
        self.orchestrator = OrchestratorAgent(self.context)
        self.marketing = MarketingAgent(self.context)
        self.market_intel = MarketIntelligenceAgent(self.context)
        self.customer_success = CustomerSuccessAgent(self.context)
        self.analytics = AnalyticsAgent(self.context)

        self._agents = [
            self.orchestrator,
            self.marketing,
            self.market_intel,
            self.customer_success,
            self.analytics,
        ]

        # Expose interaction interfaces
        self.admin = AdminInterface(
            orchestrator=self.orchestrator,
            marketing=self.marketing,
            market_intel=self.market_intel,
            customer_success=self.customer_success,
            analytics=self.analytics,
        )
        self.user = UserInterface(
            market_intel=self.market_intel,
            customer_success=self.customer_success,
            marketing=self.marketing,
        )

    def start(self) -> None:
        """Start all agents and the background scheduler."""
        for agent in self._agents:
            agent.start()
        scheduler.start()
        logger.info(
            "%s platform started with %d agents", config.PLATFORM_NAME, len(self._agents)
        )

    def stop(self) -> None:
        """Stop the background scheduler."""
        scheduler.stop()
        logger.info("%s platform stopped", config.PLATFORM_NAME)

    def agent_names(self) -> list[str]:
        """Return the names of all registered agents."""
        return [a.AGENT_NAME for a in self._agents]
