"""MCP Bootstrap - Tool Registry Initialization.

Registers all adapters at application startup and provides
access to the initialized registry.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from mcp.registry import ToolRegistry, get_registry
from mcp.adapters import (
    MarketDataAdapter,
    SignalsAdapter,
    ConsensusAdapter,
    AlertsAdapter,
    BriefsAdapter,
    AnalyticsAdapter,
    MarketIntelAdapter,
    SupportAdapter,
    MarketingAdapter,
    AdminAdapter,
)

logger = logging.getLogger(__name__)

# Adapter configuration: (name, adapter_class)
ADAPTERS = [
    ("market_data", MarketDataAdapter),
    ("signals", SignalsAdapter),
    ("consensus", ConsensusAdapter),
    ("alerts", AlertsAdapter),
    ("briefs", BriefsAdapter),
    ("analytics", AnalyticsAdapter),
    ("market_intel", MarketIntelAdapter),
    ("support", SupportAdapter),
    ("marketing", MarketingAdapter),
    ("admin", AdminAdapter),
]


def bootstrap_mcp(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """Bootstrap the MCP tool registry with all adapters.
    
    Registers all service adapters with the global (or provided) registry.
    This should be called at application startup.
    
    Args:
        registry: Optional registry to use (defaults to global registry)
    
    Returns:
        The initialized ToolRegistry
    """
    if registry is None:
        registry = get_registry()
    
    logger.info("Bootstrapping MCP tool registry...")
    
    for name, adapter_class in ADAPTERS:
        try:
            adapter = adapter_class()
            registry.register_adapter(name, adapter)
            logger.debug(f"Registered adapter: {name}")
        except Exception as e:
            logger.error(f"Failed to register adapter {name}: {e}")
    
    # Log summary
    tool_count = len(registry.list_tool_names())
    adapter_count = len(registry.list_adapter_names())
    logger.info(
        f"MCP bootstrap complete: {adapter_count} adapters, {tool_count} tools"
    )
    
    return registry


def get_available_tools() -> List[str]:
    """Get list of all available tool names.
    
    Returns:
        List of tool names (e.g., ["market_data.fetch_assets", ...])
    """
    return get_registry().list_tool_names()


def get_tool_definitions() -> List[Dict]:
    """Get all tool definitions for the coordinator.
    
    Returns:
        List of tool definition dicts
    """
    return [tool.to_dict() for tool in get_registry().list_tools()]


def get_adapter(name: str):
    """Get an adapter by name.
    
    Args:
        name: The adapter name (e.g., "market_data")
    
    Returns:
        The adapter instance or None
    """
    return get_registry().get_adapter(name)


def init_coordinator_with_mcp():
    """Initialize the coordinator with the MCP registry.
    
    Bootstraps MCP and configures the coordinator engine.
    """
    from coordinator.engine import init_coordinator
    
    # Bootstrap MCP
    registry = bootstrap_mcp()
    
    # Build tool lookup for coordinator
    tool_lookup = {}
    for tool_name in registry.list_tool_names():
        adapter = registry.get_adapter_for_tool(tool_name)
        if adapter:
            tool_lookup[tool_name] = adapter
            # Also register by prefix for quick lookup
            prefix = tool_name.split(".")[0]
            if prefix not in tool_lookup:
                tool_lookup[prefix] = adapter
    
    # Initialize coordinator with tools
    coordinator = init_coordinator(tool_registry=tool_lookup)
    
    logger.info("Coordinator initialized with MCP tools")
    
    return coordinator


# Auto-register when imported (lazy initialization)
_initialized = False


def ensure_initialized():
    """Ensure MCP is initialized (idempotent)."""
    global _initialized
    if not _initialized:
        bootstrap_mcp()
        _initialized = True
