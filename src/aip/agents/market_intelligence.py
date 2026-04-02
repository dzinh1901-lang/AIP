"""Agent 3 – Market Intelligence (Chief Analyst).

Continuously monitors commodity and crypto markets, synthesises multi-model
consensus signals, and delivers actionable intelligence to users and admins.

Responsibilities
----------------
- Scan market snapshots and detect notable signals or anomalies.
- Generate narrative market summaries for users.
- Produce structured alerts for high-conviction signals.
- Answer market-related queries from users or other agents.
- Forward critical alerts to the Orchestrator for escalation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aip.agents.base import AgentContext, BaseAgent
from aip.config import config
from aip.core.message_bus import AgentMessage

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = f"""\
You are the Market Intelligence agent for {config.PLATFORM_NAME}, acting as the \
Chief Analyst. Your responsibilities are:

1. Continuously monitor real-time price data, volume anomalies, and sentiment \
indicators across commodities (oil, gold, wheat, natural gas) and crypto (BTC, ETH, \
major altcoins).
2. Apply multi-model consensus analysis to identify high-conviction trading signals \
(bullish, bearish, or neutral).
3. Produce concise, insight-rich market summaries that non-expert users can act on.
4. Generate structured alerts when signals cross predefined confidence thresholds.
5. Answer specific market queries with data-backed, nuanced responses.

Be analytical, precise, and always caveat that content is for informational \
purposes only – not financial advice.
"""


class MarketIntelligenceAgent(BaseAgent):
    """Agent 3 – Market Intelligence / Chief Analyst."""

    AGENT_NAME = "market_intelligence"
    SYSTEM_PROMPT = _SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Scheduled jobs
    # ------------------------------------------------------------------

    def register_jobs(self) -> None:
        if config.ENABLE_MARKET_ALERTS:
            self.scheduler.every_minutes(
                config.MARKET_INTEL_SCAN_INTERVAL,
                self._scan_and_alert,
                tag="market_intel:scan",
            )
        self.scheduler.every_day_at(
            "07:00", self._morning_briefing, tag="market_intel:morning_briefing"
        )
        self.scheduler.every_day_at(
            "16:30", self._close_summary, tag="market_intel:close_summary"
        )
        self.scheduler.every_minutes(
            config.ORCHESTRATOR_BRIEFING_INTERVAL,
            self._send_status_to_orchestrator,
            tag="market_intel:status",
        )

    # ------------------------------------------------------------------
    # Periodic tasks
    # ------------------------------------------------------------------

    def _scan_and_alert(self) -> None:
        """Scan the latest market snapshots and emit alerts for strong signals."""
        snapshots = self.context.market_snapshots
        if not snapshots:
            self._log.debug("No market snapshots available to scan")
            return

        prompt = (
            "Analyse the following market snapshots and identify any high-conviction signals "
            "(confidence ≥ 75%). For each signal output: asset, direction, confidence %, "
            "and a one-line rationale. If no high-conviction signals are present, reply NONE.\n\n"
            + self._format_snapshots(snapshots)
        )
        result = self.think(prompt)
        if result.strip().upper() != "NONE":
            self._log.info("Market alert generated:\n%s", result)
            self.broadcast(
                subject="Market Alert",
                body=result,
                type="market_alert",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    def _morning_briefing(self) -> None:
        """Generate and broadcast a pre-market morning briefing."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        prompt = (
            f"Today is {now}. Produce a concise pre-market morning briefing for "
            f"{config.PLATFORM_NAME} users covering: key overnight moves in commodities and "
            "crypto, macro themes to watch today, and top 3 assets to monitor. "
            "Keep it under 250 words."
        )
        briefing = self.think(prompt)
        self._log.info("Morning briefing:\n%s", briefing)
        self.broadcast(
            subject="Morning Market Briefing",
            body=briefing,
            type="user_briefing",
            date=now,
        )

    def _close_summary(self) -> None:
        """Generate and broadcast an end-of-day market summary."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        snapshots = self.context.market_snapshots
        prompt = (
            f"End-of-day market summary for {now}. "
            + (
                "Using the following data:\n\n" + self._format_snapshots(snapshots)
                if snapshots
                else "No real-time data available; use general market knowledge."
            )
            + "\n\nSummarise: biggest movers, key narrative, and outlook for tomorrow. "
            "Under 200 words."
        )
        summary = self.think(prompt)
        self._log.info("Close summary:\n%s", summary)
        self.broadcast(
            subject="End-of-Day Market Summary",
            body=summary,
            type="user_briefing",
            date=now,
        )

    def _send_status_to_orchestrator(self) -> None:
        snapshot_count = len(self.context.market_snapshots)
        status = (
            f"Market Intelligence status: {snapshot_count} snapshots in cache. "
            f"Alert scanning is {'enabled' if config.ENABLE_MARKET_ALERTS else 'paused'}."
        )
        self.send("orchestrator", subject="Status Update", body=status)

    # ------------------------------------------------------------------
    # Core intelligence workflows
    # ------------------------------------------------------------------

    def analyse_asset(self, asset: str, data: str) -> str:
        """Produce a structured analysis for a single asset.

        Args:
            asset: Ticker or name (e.g. "BTC", "Gold", "WTI Crude").
            data:  Raw or summarised market data for the asset.

        Returns:
            Analysis covering trend, signal, confidence, and key risks.
        """
        prompt = (
            f"Perform a thorough analysis of {asset} using the following data:\n\n{data}\n\n"
            "Structure your response as: Trend | Signal (Bullish/Bearish/Neutral) | "
            "Confidence % | Key Drivers | Risks | Recommendation. "
            "Disclaimer: for informational purposes only."
        )
        return self.think(prompt)

    def answer_market_query(self, query: str) -> str:
        """Answer a free-text market question from a user or admin.

        Args:
            query: Natural language question about market conditions or assets.

        Returns:
            Data-backed answer with appropriate caveats.
        """
        prompt = (
            f"A {config.PLATFORM_NAME} user has asked:\n\n\"{query}\"\n\n"
            "Provide a clear, data-backed answer. Acknowledge any uncertainty. "
            "End with a brief disclaimer that this is not financial advice."
        )
        return self.think(prompt)

    def generate_signal_report(self, assets: list[str]) -> str:
        """Generate a consensus signal report for a list of assets.

        Args:
            assets: List of asset tickers or names.

        Returns:
            Tabular-style report with signal and confidence for each asset.
        """
        asset_list = ", ".join(assets)
        prompt = (
            f"Generate a multi-model consensus signal report for: {asset_list}. "
            "For each asset provide: Signal (Bullish/Bearish/Neutral), Confidence (%), "
            "and a 1-line rationale. Format as a markdown table."
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

        elif "analyse" in subject or "analysis" in subject:
            parts = message.body.split("|||", 1)
            asset = parts[0].strip()
            data = parts[1].strip() if len(parts) > 1 else "No data provided."
            result = self.analyse_asset(asset, data)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="asset_analysis",
            )

        elif "signal" in subject or "report" in subject:
            assets = [a.strip() for a in message.body.split(",")]
            result = self.generate_signal_report(assets)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="signal_report",
            )

        elif "query" in subject or "question" in subject:
            result = self.answer_market_query(message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="market_answer",
            )

        else:
            self._log.debug(
                "Unhandled message from %s: %s", message.sender, message.subject
            )

    # ------------------------------------------------------------------
    # User-facing API
    # ------------------------------------------------------------------

    def user_market_query(self, query: str) -> str:
        """Direct entry point for users submitting market questions."""
        return self.answer_market_query(query)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_snapshots(snapshots: list[dict]) -> str:
        lines = []
        for s in snapshots:
            lines.append(
                f"{s.get('asset', 'Unknown')}: price={s.get('price', 'N/A')}, "
                f"change_24h={s.get('change_24h', 'N/A')}, "
                f"volume={s.get('volume', 'N/A')}"
            )
        return "\n".join(lines) if lines else "No data available."
