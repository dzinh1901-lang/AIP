"""MCP Adapters Package.

Adapters that wrap existing services with MCP-compatible interfaces.
Each adapter provides tool definitions and invocation methods.
"""

from mcp.adapters.market_data import MarketDataAdapter
from mcp.adapters.signals import SignalsAdapter
from mcp.adapters.consensus import ConsensusAdapter
from mcp.adapters.alerts import AlertsAdapter
from mcp.adapters.briefs import BriefsAdapter
from mcp.adapters.analytics import AnalyticsAdapter
from mcp.adapters.market_intel import MarketIntelAdapter
from mcp.adapters.support import SupportAdapter
from mcp.adapters.marketing import MarketingAdapter
from mcp.adapters.admin import AdminAdapter

__all__ = [
    "MarketDataAdapter",
    "SignalsAdapter",
    "ConsensusAdapter",
    "AlertsAdapter",
    "BriefsAdapter",
    "AnalyticsAdapter",
    "MarketIntelAdapter",
    "SupportAdapter",
    "MarketingAdapter",
    "AdminAdapter",
]
