"""MCP (Model Context Protocol) Adapter Layer.

This module provides MCP-compatible tool abstractions for the existing
Global Market Intelligence services. Each adapter wraps existing business
logic without modifying it, providing a standardized interface for the
coordinator to invoke capabilities.

Key Components:
- types.py: MCP-compatible type definitions (Tool, ToolInput, ToolResult)
- registry.py: Tool registry with discovery and lookup
- client.py: MCP client interface for invoking tools
- adapters/: Service-specific adapters that wrap existing functionality

Design Principles:
- Adapters are pure wrappers - no business logic modifications
- Explicit tool contracts via Tool schema
- Consistent error handling via ToolError
- Support for tool validation and documentation
"""

from mcp.types import (
    Tool,
    ToolInput,
    ToolResult,
    ToolError,
    ToolCapability,
)
from mcp.registry import (
    ToolRegistry,
    get_registry,
    register_adapter,
)
from mcp.client import (
    MCPClient,
    get_mcp_client,
)

__all__ = [
    # Types
    "Tool",
    "ToolInput",
    "ToolResult",
    "ToolError",
    "ToolCapability",
    # Registry
    "ToolRegistry",
    "get_registry",
    "register_adapter",
    # Client
    "MCPClient",
    "get_mcp_client",
]
