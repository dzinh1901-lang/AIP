"""Agent 4 – Customer Success Manager.

Manages the full user lifecycle on the AIP platform: onboarding,
engagement, retention, and support escalation.

Responsibilities
----------------
- Welcome and onboard new users with personalised guidance.
- Proactively reach out to at-risk or inactive users.
- Answer platform usage questions and route complex issues.
- Collect user feedback and surface insights to the Orchestrator.
- Celebrate user milestones to drive engagement and loyalty.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from aip.agents.base import AgentContext, BaseAgent
from aip.config import config
from aip.core.message_bus import AgentMessage

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = f"""\
You are the Customer Success Manager agent for {config.PLATFORM_NAME}, an AI-powered \
market intelligence platform for commodities and crypto. Your responsibilities are:

1. Welcome new users with a warm, personalised onboarding experience that helps \
them realise value quickly.
2. Monitor user engagement and proactively reach out to users who appear disengaged \
or at risk of churning.
3. Answer platform usage questions clearly and concisely.
4. Collect and synthesise user feedback to identify product improvement opportunities.
5. Escalate complex technical or billing issues to the appropriate team.

Use a helpful, empathetic, and knowledgeable tone. Always put the user's success first.
"""


class CustomerSuccessAgent(BaseAgent):
    """Agent 4 – Customer Success Manager."""

    AGENT_NAME = "customer_success"
    SYSTEM_PROMPT = _SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Scheduled jobs
    # ------------------------------------------------------------------

    def register_jobs(self) -> None:
        self.scheduler.every_minutes(
            config.CUSTOMER_SUCCESS_CHECK_INTERVAL,
            self._check_user_engagement,
            tag="customer_success:engagement_check",
        )
        self.scheduler.every_day_at(
            "10:00", self._send_status_to_orchestrator, tag="customer_success:daily_status"
        )

    # ------------------------------------------------------------------
    # Periodic tasks
    # ------------------------------------------------------------------

    def _check_user_engagement(self) -> None:
        """Identify and reach out to inactive or at-risk users."""
        users = self.context.active_users
        if not users:
            self._log.debug("No active users to check")
            return

        at_risk = [u for u in users if u.get("days_since_login", 0) >= 7]
        for user in at_risk[:5]:  # process up to 5 per cycle
            message = self.compose_reengagement(user)
            self._log.info(
                "Re-engagement message for %s:\n%s", user.get("email", "unknown"), message
            )

    def _send_status_to_orchestrator(self) -> None:
        user_count = len(self.context.active_users)
        at_risk = sum(
            1 for u in self.context.active_users if u.get("days_since_login", 0) >= 7
        )
        status = (
            f"Customer Success status: {user_count} active users, "
            f"{at_risk} at-risk (inactive ≥7 days)."
        )
        self.send("orchestrator", subject="Status Update", body=status)

    # ------------------------------------------------------------------
    # Core customer success workflows
    # ------------------------------------------------------------------

    def onboard_user(self, user: dict) -> str:
        """Generate a personalised onboarding message for a new user.

        Args:
            user: Dict with keys ``name``, ``email``, ``interest``
                  (e.g. "crypto", "commodities", "both"), and optionally
                  ``experience_level`` ("beginner", "intermediate", "expert").

        Returns:
            Personalised welcome and onboarding guidance message.
        """
        name = user.get("name", "there")
        interest = user.get("interest", "markets")
        level = user.get("experience_level", "intermediate")
        prompt = (
            f"Write a warm onboarding welcome message for a new {config.PLATFORM_NAME} user "
            f"named {name}. They are interested in {interest} and consider themselves a "
            f"{level} trader/investor. "
            "Cover: 3 key features to start with, one quick win they can achieve today, "
            "and an invitation to reach out with questions. Under 200 words."
        )
        return self.think(prompt)

    def compose_reengagement(self, user: dict) -> str:
        """Create a re-engagement message for an inactive user.

        Args:
            user: Dict with ``name``, ``email``, and ``days_since_login``.

        Returns:
            Personalised re-engagement message.
        """
        name = user.get("name", "there")
        days = user.get("days_since_login", 7)
        prompt = (
            f"Write a friendly re-engagement message for {config.PLATFORM_NAME} user {name}, "
            f"who hasn't logged in for {days} days. "
            "Remind them of a relevant feature or recent market insight they missed. "
            "Include a clear call to action. Under 120 words."
        )
        return self.think(prompt)

    def answer_support_query(self, user: dict, query: str) -> str:
        """Answer a user's platform support or usage question.

        Args:
            user:  Dict with at minimum ``name``.
            query: The user's question as a string.

        Returns:
            Clear, helpful answer. Escalation guidance included if needed.
        """
        name = user.get("name", "User")
        prompt = (
            f"{name} asks: \"{query}\"\n\n"
            f"Respond as the {config.PLATFORM_NAME} Customer Success Manager. "
            "If the question is about platform features, explain clearly. "
            "If it requires escalation (billing, data errors, outages), say so and "
            "describe the next steps. Keep the tone warm and under 150 words."
        )
        return self.think(prompt)

    def collect_feedback(self, user: dict, feedback: str) -> str:
        """Process user feedback and generate an acknowledgement + internal summary.

        Args:
            user:     Dict with ``name`` and ``email``.
            feedback: Raw feedback text from the user.

        Returns:
            A tuple-like response string: acknowledgement + insight summary.
        """
        name = user.get("name", "User")
        prompt = (
            f"User {name} has submitted the following feedback about {config.PLATFORM_NAME}:\n\n"
            f"\"{feedback}\"\n\n"
            "1. Write a warm acknowledgement reply to the user (2-3 sentences).\n"
            "2. Write a brief internal insight note for the product team (bullet points). "
            "Separate these sections with '---'."
        )
        return self.think(prompt)

    def celebrate_milestone(self, user: dict, milestone: str) -> str:
        """Generate a milestone celebration message for an engaged user.

        Args:
            user:      Dict with ``name``.
            milestone: Description of the milestone (e.g. "30-day streak", "first alert fired").

        Returns:
            Celebratory message with a next-step nudge.
        """
        name = user.get("name", "there")
        prompt = (
            f"Write a short celebration message for {config.PLATFORM_NAME} user {name} "
            f"who just achieved: {milestone}. "
            "Be genuine, brief (under 80 words), and include a next challenge or feature to explore."
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

        elif "onboard" in subject:
            import json
            try:
                user = json.loads(message.body)
            except (ValueError, TypeError):
                user = {"name": message.body}
            result = self.onboard_user(user)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="onboarding_message",
            )

        elif "feedback" in subject:
            result = self.collect_feedback({"name": message.sender}, message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="feedback_processed",
            )

        elif "support" in subject or "help" in subject or "question" in subject:
            result = self.answer_support_query({"name": message.sender}, message.body)
            self.send(
                message.sender,
                subject=f"Re: {message.subject}",
                body=result,
                type="support_response",
            )

        else:
            self._log.debug(
                "Unhandled message from %s: %s", message.sender, message.subject
            )

    # ------------------------------------------------------------------
    # User-facing API
    # ------------------------------------------------------------------

    def user_support_query(self, user: dict, query: str) -> str:
        """Direct entry point for users submitting support questions."""
        return self.answer_support_query(user, query)

    def user_feedback(self, user: dict, feedback: str) -> str:
        """Direct entry point for users submitting feedback."""
        return self.collect_feedback(user, feedback)
