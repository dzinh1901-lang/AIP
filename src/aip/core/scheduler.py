"""Recurring-task scheduler for agent daily workflows.

Wraps the ``schedule`` library with a simple registration API so each
agent can declare its own cadence without coupling to the scheduler
implementation.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Callable

import schedule

logger = logging.getLogger(__name__)


class AgentScheduler:
    """Runs registered periodic jobs on a background daemon thread."""

    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def every_minutes(self, minutes: int, job: Callable[[], None], *, tag: str = "") -> None:
        """Schedule *job* to run every *minutes* minutes."""
        entry = schedule.every(minutes).minutes.do(job)
        if tag:
            entry.tag(tag)
        logger.debug("Scheduled '%s' every %d minute(s)", tag or job.__name__, minutes)

    def every_day_at(self, time_str: str, job: Callable[[], None], *, tag: str = "") -> None:
        """Schedule *job* to run once per day at *time_str* (e.g. '09:00')."""
        entry = schedule.every().day.at(time_str).do(job)
        if tag:
            entry.tag(tag)
        logger.debug("Scheduled '%s' daily at %s", tag or job.__name__, time_str)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background scheduler thread (idempotent)."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="AgentScheduler")
        self._thread.start()
        logger.info("AgentScheduler started")

    def stop(self) -> None:
        """Signal the scheduler thread to stop and wait for it."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("AgentScheduler stopped")

    def run_pending(self) -> None:
        """Manually trigger all pending jobs (useful in tests)."""
        schedule.run_pending()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)


# Module-level singleton.
scheduler = AgentScheduler()
