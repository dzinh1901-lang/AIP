"""Platform-wide configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # LLM backend
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    # Platform identity
    PLATFORM_NAME: str = os.getenv("PLATFORM_NAME", "AIP")

    # Scheduler intervals (minutes)
    ORCHESTRATOR_BRIEFING_INTERVAL: int = int(
        os.getenv("ORCHESTRATOR_BRIEFING_INTERVAL", "60")
    )
    MARKETING_CADENCE_INTERVAL: int = int(
        os.getenv("MARKETING_CADENCE_INTERVAL", "120")
    )
    MARKET_INTEL_SCAN_INTERVAL: int = int(
        os.getenv("MARKET_INTEL_SCAN_INTERVAL", "30")
    )
    CUSTOMER_SUCCESS_CHECK_INTERVAL: int = int(
        os.getenv("CUSTOMER_SUCCESS_CHECK_INTERVAL", "60")
    )
    ANALYTICS_REPORT_INTERVAL: int = int(
        os.getenv("ANALYTICS_REPORT_INTERVAL", "240")
    )

    # Feature flags
    ENABLE_DAILY_BRIEFING: bool = os.getenv("ENABLE_DAILY_BRIEFING", "true").lower() == "true"
    ENABLE_LEAD_GENERATION: bool = os.getenv("ENABLE_LEAD_GENERATION", "true").lower() == "true"
    ENABLE_MARKET_ALERTS: bool = os.getenv("ENABLE_MARKET_ALERTS", "true").lower() == "true"


config = Config()
