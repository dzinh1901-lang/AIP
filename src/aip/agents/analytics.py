"""Agent 5 – Analytics (Data Analyst).

Tracks platform-level performance, user behaviour, and business KPIs,
then delivers actionable insights to administrators and the Orchestrator.

Responsibilities
----------------
- Compute and report platform KPIs (DAU, retention, feature adoption).
- Generate scheduled analytics reports for admins.
- Detect anomalies in platform usage patterns.
- Answer ad-hoc data questions from admins and agents.
- Feed insights back to Marketing and Customer Success agents.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aip.agents.base import AgentContext, BaseAgent
from aip.config import config
from aip.core.message_bus import AgentMessage

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = f"""\
You are the Analytics agent for {config.PLATFORM_NAME}, acting as the platform's \
Data Analyst. Your responsibilities are:

1. Track and report key platform metrics: daily active users (DAU), weekly active \
users (WAU), user retention rates, feature adoption, and alert engagement.
2. Produce clear, visual-friendly analytics reports for administrators (markdown tables, \
bullet summaries).
3. Identify anomalies and unusual patterns in usage data that warrant investigation.
4. Answer ad-hoc data questions with precision and appropriate context.
5. Share actionable insights with the Marketing and Customer Success agents to \
optimise their workflows.

Be rigorous, data-first, and translate numbers into clear business implications.
"""


class AnalyticsAgent(BaseAgent):
    """Agent 5 – Analytics / Data Analyst."""

    AGENT_NAME = "analytics"
    SYSTEM_PROMPT = _SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Scheduled jobs
    # ------------------------------------------------------------------

    def register_jobs(self) -> None:
        self.scheduler.every_minutes(
            config.ANALYTICS_REPORT_INTERVAL,
            self._periodic_report,
            tag="analytics:periodic_report",
        )
        self.scheduler.every_day_at(
            "08:00", self._daily_kpi_report, tag="analytics:daily_kpi"
        )
        self.scheduler.every_day_at(
            "08:05", self._send_status_to_orchestrator, tag="analytics:daily_status"
        )

    # ------------------------------------------------------------------
    # Periodic tasks
    # ------------------------------------------------------------------

    def _periodic_report(self) -> None:
        """Generate and broadcast a periodic platform analytics snapshot."""
        report = self.generate_platform_snapshot()
        self._log.info("Periodic analytics snapshot:\n%s", report)
        self.send(
            "orchestrator",
            subject="Analytics Snapshot",
            body=report,
            type="analytics_snapshot",
        )

    def _daily_kpi_report(self) -> None:
        """Generate and broadcast the daily KPI report."""
        report = self.generate_kpi_report()
        self._log.info("Daily KPI report:\n%s", report)
        self.broadcast(
            subject="Daily KPI Report",
            body=report,
            type="kpi_report",
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )

    def _send_status_to_orchestrator(self) -> None:
        user_count = len(self.context.active_users)
        status = (
            f"Analytics status: monitoring {user_count} users. "
            "Daily KPI report generated."
        )
        self.send("orchestrator", subject="Status Update", body=status)

    # ------------------------------------------------------------------
    # Core analytics workflows
    # ------------------------------------------------------------------

    def generate_platform_snapshot(self) -> str:
        """Generate a real-time snapshot of platform health metrics.

        Returns:
            Markdown-formatted snapshot covering users, leads, and market data.
        """
        users = self.context.active_users
        leads = self.context.active_leads
        snapshots = self.context.market_snapshots
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        context_str = (
            f"Snapshot time: {now}\n"
            f"Active users: {len(users)}\n"
            f"Active leads in CRM: {len(leads)}\n"
            f"Market snapshots cached: {len(snapshots)}\n"
        )
        if users:
            at_risk = sum(1 for u in users if u.get("days_since_login", 0) >= 7)
            context_str += f"At-risk users (inactive ≥7d): {at_risk}\n"

        prompt = (
            f"Generate a platform health snapshot for {config.PLATFORM_NAME} administrators "
            f"based on these metrics:\n\n{context_str}\n\n"
            "Format as a concise markdown report with sections: Overview, User Health, "
            "Pipeline, and Recommendations."
        )
        return self.think(prompt)

    def generate_kpi_report(self) -> str:
        """Generate a daily KPI report.

        Returns:
            Structured markdown KPI report covering growth, retention, and engagement.
        """
        users = self.context.active_users
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        user_stats = f"{len(users)} total active users"
        if users:
            new_today = sum(1 for u in users if u.get("joined_today", False))
            at_risk = sum(1 for u in users if u.get("days_since_login", 0) >= 7)
            user_stats += f", {new_today} joined today, {at_risk} at risk"

        prompt = (
            f"Generate a daily KPI report for {config.PLATFORM_NAME} for {now}. "
            f"User data: {user_stats}. "
            "Include: DAU trend, retention signal, top features by engagement (estimated), "
            "growth vs prior period (estimated), and 3 actionable recommendations. "
            "Format as markdown with a summary table."
        )
        return self.think(prompt)

    def detect_anomalies(self, metrics: dict) -> str:
        """Detect anomalies in a provided metrics dictionary.

        Args:
            metrics: Dict of metric_name → value (or list of values for time series).

        Returns:
            Anomaly report listing any unusual patterns with severity and recommendation.
        """
        metrics_str = "\n".join(f"- {k}: {v}" for k, v in metrics.items())
        prompt = (
            f"Analyse the following platform metrics for {config.PLATFORM_NAME} and identify "
            f"anomalies or concerning patterns:\n\n{metrics_str}\n\n"
            "For each anomaly found: name it, classify severity (Low/Medium/High), "
            "suggest a likely cause, and recommend an action. "
            "If no anomalies are found, say 'No anomalies detected.'"
        )
        return self.think(prompt)

    def answer_data_query(self, query: str) -> str:
        """Answer an ad-hoc analytics or data question from an admin or agent.

        Args:
            query: Natural language data question.

        Returns:
            Data-informed answer with appropriate caveats.
        """
        users = self.context.active_users
        leads = self.context.active_leads
        context_str = (
            f"Platform context: {len(users)} active users, {len(leads)} leads in CRM."
        )
        prompt = (
            f"Analytics question: \"{query}\"\n\n"
            f"{context_str}\n\n"
            "Answer precisely. If the exact data is not available, provide the best "
            "estimate with clear assumptions stated."
        )
        return self.think(prompt)

    def segment_users(self, criteria: str) -> str:
        """Segment the user base based on specified criteria.

        Args:
            criteria: Description of the segmentation approach
                      (e.g. "by interest: crypto vs commodities vs both").

        Returns:
            Segmentation analysis with counts and recommended actions per segment.
        """
        users = self.context.active_users
        prompt = (
            f"Segment the {len(users)} {config.PLATFORM_NAME} users by: {criteria}.\n\n"
            "Available user data: " + (
                str([{k: u.get(k) for k in ("name", "interest", "days_since_login", "joined_today")}
                     for u in users[:20]])
                if users else "No user data available."
            )
            + "\n\nProvide: segment names, estimated sizes, key characteristics, "
            "and one tailored action for each segment."
        )
        return self.think(prompt)

    # ------------------------------------------------------------------
    # Message handling
    # ------------------------------------------------------------------

    def handle_message(self, message: AgentMessage) -> None:
        if message.recipient not in (self.AGENT_NAME, "broadcast"):
            return

        subject = message.subject.lower()

        if "status request" in subject:
            self._send_status_to_orchestrator()

        elif "kpi" in subject or "report" in subject:
            result = self.generate_kpi_report()
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="kpi_report",
            )

        elif "anomal" in subject:
            import json
            try:
                metrics = json.loads(message.body)
            except (ValueError, TypeError):
                metrics = {"raw_input": message.body}
            result = self.detect_anomalies(metrics)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="anomaly_report",
            )

        elif "segment" in subject:
            result = self.segment_users(message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="user_segmentation",
            )

        elif "query" in subject or "data" in subject:
            result = self.answer_data_query(message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="data_answer",
            )

        else:
            self._log.debug(
                "Unhandled message from %s: %s", message.sender, message.subject
            )

    # ------------------------------------------------------------------
    # Admin-facing API
    # ------------------------------------------------------------------

    def admin_data_query(self, query: str) -> str:
        """Direct entry point for admin data queries."""
        return self.answer_data_query(query)
