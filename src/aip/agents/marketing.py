"""Agent 2 – Marketing Director & Lead Generation.

Drives top-of-funnel growth for the AIP platform through automated
lead generation, personalised outreach content, and campaign management.

Responsibilities
----------------
- Generate targeted outreach content for commodities and crypto audiences.
- Qualify inbound leads and build nurture sequences.
- Report campaign performance metrics to the Orchestrator.
- Respond to admin requests for marketing copy and campaign plans.
- Engage users with relevant market updates to drive retention.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aip.agents.base import AgentContext, BaseAgent
from aip.config import config
from aip.core.message_bus import AgentMessage

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = f"""\
You are the Marketing Director agent for {config.PLATFORM_NAME}, an AI-powered \
market intelligence platform for commodities and crypto. Your responsibilities are:

1. Develop and execute lead generation strategies targeting traders, investors, \
and financial professionals.
2. Create compelling, data-driven marketing copy, email sequences, and social \
content that highlights real-time intelligence features.
3. Qualify leads based on their interest level and market focus (commodities vs crypto).
4. Design multi-touch nurture campaigns that move prospects through the funnel.
5. Report weekly campaign metrics and pipeline updates to the Orchestrator.

Communicate with a professional yet energetic tone. Emphasise data, ROI, and \
competitive advantage in every message.
"""


class MarketingAgent(BaseAgent):
    """Agent 2 – Marketing Director & Lead Generation."""

    AGENT_NAME = "marketing"
    SYSTEM_PROMPT = _SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Scheduled jobs
    # ------------------------------------------------------------------

    def register_jobs(self) -> None:
        if config.ENABLE_LEAD_GENERATION:
            self.scheduler.every_minutes(
                config.MARKETING_CADENCE_INTERVAL,
                self._lead_gen_cycle,
                tag="marketing:lead_gen",
            )
        self.scheduler.every_day_at(
            "08:30", self._send_status_to_orchestrator, tag="marketing:daily_status"
        )

    # ------------------------------------------------------------------
    # Periodic tasks
    # ------------------------------------------------------------------

    def _lead_gen_cycle(self) -> None:
        """Generate outreach content for the current lead pool."""
        leads = self.context.active_leads
        if not leads:
            self._log.info("No active leads to process this cycle")
            return

        for lead in leads[:10]:  # process up to 10 leads per cycle
            content = self.generate_outreach(lead)
            self._log.info(
                "Generated outreach for lead %s:\n%s", lead.get("email", "unknown"), content
            )

    def _send_status_to_orchestrator(self) -> None:
        """Send daily status update to the Orchestrator."""
        lead_count = len(self.context.active_leads)
        status = (
            f"Marketing status: {lead_count} active leads in pipeline. "
            f"Lead generation is {'enabled' if config.ENABLE_LEAD_GENERATION else 'paused'}."
        )
        self.send("orchestrator", subject="Status Update", body=status)

    # ------------------------------------------------------------------
    # Core marketing workflows
    # ------------------------------------------------------------------

    def generate_outreach(self, lead: dict) -> str:
        """Generate personalised outreach content for a specific lead.

        Args:
            lead: Dict with keys such as ``name``, ``email``, ``interest``
                  (e.g. "commodities", "crypto", "both"), and ``stage``
                  (e.g. "cold", "warm", "hot").

        Returns:
            A personalised outreach email or message body.
        """
        name = lead.get("name", "there")
        interest = lead.get("interest", "commodities and crypto")
        stage = lead.get("stage", "cold")
        prompt = (
            f"Write a personalised outreach email for a {stage} lead named {name} who is "
            f"interested in {interest} markets. "
            f"Highlight {config.PLATFORM_NAME}'s real-time intelligence and consensus signals. "
            "Keep it under 150 words. Use a subject line and sign off as the platform team."
        )
        return self.think(prompt)

    def create_campaign(self, campaign_brief: str) -> str:
        """Create a multi-touch campaign plan from a brief.

        Args:
            campaign_brief: High-level description of the campaign goal and audience.

        Returns:
            A structured campaign plan with touchpoints, messaging, and KPIs.
        """
        prompt = (
            f"Create a 5-touchpoint digital marketing campaign for {config.PLATFORM_NAME} "
            f"based on this brief:\n\n{campaign_brief}\n\n"
            "For each touchpoint specify: channel, timing, message, and success metric."
        )
        return self.think(prompt)

    def qualify_lead(self, lead_info: str) -> str:
        """Assess a lead's qualification score and recommended next step.

        Args:
            lead_info: Free-text description of the lead (source, behaviour, stated needs).

        Returns:
            Qualification assessment with score (Cold/Warm/Hot) and next-step recommendation.
        """
        prompt = (
            f"Evaluate the following lead for {config.PLATFORM_NAME} and assign a score "
            f"(Cold / Warm / Hot). Provide a one-sentence rationale and recommended next step.\n\n"
            f"Lead info: {lead_info}"
        )
        return self.think(prompt)

    def generate_social_post(self, market_highlight: str) -> str:
        """Create a social media post based on a market highlight.

        Args:
            market_highlight: A brief description of a notable market event or signal.

        Returns:
            Platform-appropriate social post text (LinkedIn/Twitter style).
        """
        prompt = (
            f"Write a short, engaging social media post (≤280 characters) for "
            f"{config.PLATFORM_NAME} based on this market highlight:\n\n{market_highlight}\n\n"
            "Include a call-to-action to try the platform."
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

        elif "campaign" in subject:
            result = self.create_campaign(message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="campaign_plan",
            )

        elif "lead" in subject:
            result = self.qualify_lead(message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="lead_qualification",
            )

        elif "social" in subject or "post" in subject:
            result = self.generate_social_post(message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="social_post",
            )

        else:
            self._log.debug(
                "Unhandled message from %s: %s", message.sender, message.subject
            )

    # ------------------------------------------------------------------
    # User-facing API
    # ------------------------------------------------------------------

    def user_referral_message(self, referrer_name: str, platform_benefit: str) -> str:
        """Generate a referral invitation message for an existing user to share.

        Args:
            referrer_name: Name of the existing user making the referral.
            platform_benefit: Key benefit to highlight in the invitation.

        Returns:
            A short referral message the user can send to a contact.
        """
        prompt = (
            f"Write a short referral message from {referrer_name} inviting a colleague "
            f"to join {config.PLATFORM_NAME}. Highlight: {platform_benefit}. "
            "Keep it friendly and under 80 words."
        )
        return self.think(prompt)
