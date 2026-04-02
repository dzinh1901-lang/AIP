"""Agent 1 – Orchestrator (COO).

The Orchestrator oversees all other agents, coordinates their daily
workflows, produces consolidated briefings for platform administrators,
and acts as the primary escalation point for cross-agent decisions.

Responsibilities
----------------
- Issue daily operational briefings to admins.
- Route incoming admin requests to the appropriate specialist agent.
- Collect status updates from all agents and surface anomalies.
- Make prioritisation decisions when agents report conflicts.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aip.agents.base import AgentContext, BaseAgent
from aip.config import config
from aip.core.message_bus import AgentMessage

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = f"""\
You are the Orchestrator agent for {config.PLATFORM_NAME}, acting as the \
Chief Operating Officer (COO) of the AI agent team. Your role is to:

1. Oversee and coordinate the Marketing, Market Intelligence, Customer Success, \
and Analytics agents.
2. Produce clear, executive-level daily briefings for platform administrators.
3. Route incoming tasks and escalations to the most appropriate specialist agent.
4. Identify conflicts or bottlenecks across agents and resolve them.
5. Maintain a high-level view of platform health, user satisfaction, and business \
growth metrics.

Always communicate with clarity, authority, and a bias toward action.
"""


class OrchestratorAgent(BaseAgent):
    """Agent 1 – Orchestrator / COO."""

    AGENT_NAME = "orchestrator"
    SYSTEM_PROMPT = _SYSTEM_PROMPT

    # Tracks status reports received from other agents during the current cycle.
    _status_reports: list[dict] = []

    # ------------------------------------------------------------------
    # Scheduled jobs
    # ------------------------------------------------------------------

    def register_jobs(self) -> None:
        if config.ENABLE_DAILY_BRIEFING:
            self.scheduler.every_day_at(
                "09:00", self._daily_briefing, tag="orchestrator:daily_briefing"
            )
        self.scheduler.every_minutes(
            config.ORCHESTRATOR_BRIEFING_INTERVAL,
            self._collect_agent_status,
            tag="orchestrator:status_collection",
        )

    # ------------------------------------------------------------------
    # Periodic tasks
    # ------------------------------------------------------------------

    def _daily_briefing(self) -> None:
        """Generate and broadcast the daily operational briefing."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        status_summary = self._build_status_summary()
        prompt = (
            f"Today is {now}. Generate a concise daily operational briefing for the "
            f"{config.PLATFORM_NAME} platform administrators. "
            f"Summarise the current status of all agent teams:\n\n{status_summary}\n\n"
            "Include: key highlights, risks to address today, and recommended actions."
        )
        briefing = self.think(prompt)
        self._log.info("Daily briefing generated:\n%s", briefing)
        self.broadcast(
            subject="Daily Operational Briefing",
            body=briefing,
            date=now,
            type="admin_briefing",
        )
        # Reset status cache after briefing
        self._status_reports.clear()

    def _collect_agent_status(self) -> None:
        """Request status updates from all specialist agents."""
        self.send("marketing", "Status Request", "Please provide your current status.")
        self.send("market_intelligence", "Status Request", "Please provide your current status.")
        self.send("customer_success", "Status Request", "Please provide your current status.")
        self.send("analytics", "Status Request", "Please provide your current status.")

    # ------------------------------------------------------------------
    # Message handling
    # ------------------------------------------------------------------

    def handle_message(self, message: AgentMessage) -> None:
        if message.recipient not in (self.AGENT_NAME, "broadcast"):
            return
        if message.recipient == "broadcast" and message.sender == self.AGENT_NAME:
            return  # ignore own broadcasts

        subject = message.subject.lower()

        if "status update" in subject:
            self._status_reports.append(
                {"agent": message.sender, "body": message.body, "subject": message.subject}
            )
            self._log.info("Received status update from %s", message.sender)

        elif "escalation" in subject or "alert" in subject:
            self._handle_escalation(message)

        elif "route" in subject or "request" in subject:
            self._route_request(message)

        else:
            self._log.debug("Unhandled message from %s: %s", message.sender, message.subject)

    def _handle_escalation(self, message: AgentMessage) -> None:
        prompt = (
            f"You received an escalation from the {message.sender} agent:\n\n"
            f"Subject: {message.subject}\n"
            f"Details: {message.body}\n\n"
            "Provide a recommended resolution and identify which agent should act on it."
        )
        resolution = self.think(prompt)
        self._log.warning("ESCALATION from %s – resolution:\n%s", message.sender, resolution)
        self.send(
            message.sender,
            subject=f"Re: {message.subject}",
            body=resolution,
            type="escalation_response",
        )

    def _route_request(self, message: AgentMessage) -> None:
        prompt = (
            f"A request has arrived:\n\nSubject: {message.subject}\nBody: {message.body}\n\n"
            "Based on the content, respond with ONLY the name of the most suitable agent to "
            "handle this (one of: marketing, market_intelligence, customer_success, analytics)."
        )
        target_agent = self.think(prompt).strip().lower().split()[0]
        valid_agents = {"marketing", "market_intelligence", "customer_success", "analytics"}
        if target_agent not in valid_agents:
            target_agent = "analytics"
        self._log.info("Routing request '%s' to %s", message.subject, target_agent)
        self.send(
            target_agent,
            subject=message.subject,
            body=message.body,
            routed_by="orchestrator",
            original_sender=message.sender,
        )

    # ------------------------------------------------------------------
    # Admin-facing API
    # ------------------------------------------------------------------

    def admin_query(self, query: str) -> str:
        """Handle a direct administrative query and return the response."""
        prompt = (
            f"An administrator has submitted the following query:\n\n{query}\n\n"
            "Respond as the platform COO with a clear, actionable answer. "
            "If the query requires a specialist agent, indicate which one and why."
        )
        return self.think(prompt)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_status_summary(self) -> str:
        if not self._status_reports:
            return "No status reports have been received yet in this cycle."
        lines = []
        for report in self._status_reports:
            lines.append(f"[{report['agent'].upper()}] {report['subject']}: {report['body'][:200]}")
        return "\n".join(lines)
