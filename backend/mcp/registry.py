"""MCP Tool Registry.

Central registry for all available tools. Provides discovery, lookup,
and metadata access for the coordinator engine.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

from mcp.types import Tool, ToolCapability

logger = logging.getLogger(__name__)


@runtime_checkable
class ToolAdapter(Protocol):
    """Protocol for tool adapters.
    
    Adapters must implement:
    - get_tools(): Return list of Tool definitions
    - invoke(method, params, context): Invoke a specific tool method
    """
    
    def get_tools(self) -> List[Tool]:
        """Get all tools provided by this adapter."""
        ...
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a tool method.
        
        Args:
            method: The method name (e.g., "fetch_assets" for market_data.fetch_assets)
            params: Input parameters
            context: Optional context (task state, session, etc.)
        
        Returns:
            Dict with "data" key and optional "artifacts" key
        """
        ...


class ToolRegistry:
    """Central registry for all available tools.
    
    Manages tool registration, discovery, and lookup.
    """
    
    def __init__(self):
        self._adapters: Dict[str, ToolAdapter] = {}
        self._tools: Dict[str, Tool] = {}
        self._tool_to_adapter: Dict[str, str] = {}
    
    def register_adapter(self, name: str, adapter: ToolAdapter) -> None:
        """Register a tool adapter.
        
        Args:
            name: The adapter name (e.g., "market_data")
            adapter: The adapter instance implementing ToolAdapter protocol
        """
        if not isinstance(adapter, ToolAdapter):
            logger.warning(f"Adapter {name} does not implement ToolAdapter protocol")
        
        self._adapters[name] = adapter
        
        # Register all tools from the adapter
        try:
            tools = adapter.get_tools()
            for tool in tools:
                self._tools[tool.name] = tool
                self._tool_to_adapter[tool.name] = name
            logger.info(f"Registered adapter '{name}' with {len(tools)} tools")
        except Exception as e:
            logger.error(f"Failed to register adapter {name}: {e}")
            raise
    
    def unregister_adapter(self, name: str) -> None:
        """Unregister a tool adapter.
        
        Args:
            name: The adapter name to remove
        """
        if name not in self._adapters:
            return
        
        # Remove all tools from this adapter
        tools_to_remove = [
            tool_name for tool_name, adapter_name in self._tool_to_adapter.items()
            if adapter_name == name
        ]
        for tool_name in tools_to_remove:
            del self._tools[tool_name]
            del self._tool_to_adapter[tool_name]
        
        del self._adapters[name]
        logger.info(f"Unregistered adapter '{name}'")
    
    def get_adapter(self, name: str) -> Optional[ToolAdapter]:
        """Get an adapter by name.
        
        Args:
            name: The adapter name
        
        Returns:
            The adapter instance or None if not found
        """
        return self._adapters.get(name)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool definition by name.
        
        Args:
            tool_name: The full tool name (e.g., "market_data.fetch_assets")
        
        Returns:
            The Tool definition or None if not found
        """
        return self._tools.get(tool_name)
    
    def get_adapter_for_tool(self, tool_name: str) -> Optional[ToolAdapter]:
        """Get the adapter that provides a specific tool.
        
        Args:
            tool_name: The full tool name
        
        Returns:
            The adapter instance or None if not found
        """
        adapter_name = self._tool_to_adapter.get(tool_name)
        if adapter_name:
            return self._adapters.get(adapter_name)
        return None
    
    def list_tools(
        self,
        capability: Optional[ToolCapability] = None,
        tag: Optional[str] = None,
    ) -> List[Tool]:
        """List all registered tools.
        
        Args:
            capability: Filter by capability type
            tag: Filter by tag
        
        Returns:
            List of matching Tool definitions
        """
        tools = list(self._tools.values())
        
        if capability:
            tools = [t for t in tools if t.capability == capability]
        
        if tag:
            tools = [t for t in tools if tag in t.tags]
        
        return tools
    
    def list_tool_names(self) -> List[str]:
        """Get all registered tool names."""
        return list(self._tools.keys())
    
    def list_adapter_names(self) -> List[str]:
        """Get all registered adapter names."""
        return list(self._adapters.keys())
    
    def get_tools_by_adapter(self, adapter_name: str) -> List[Tool]:
        """Get all tools provided by a specific adapter.
        
        Args:
            adapter_name: The adapter name
        
        Returns:
            List of tools from that adapter
        """
        return [
            self._tools[tool_name]
            for tool_name, name in self._tool_to_adapter.items()
            if name == adapter_name
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize registry to dictionary."""
        return {
            "adapters": list(self._adapters.keys()),
            "tools": [t.to_dict() for t in self._tools.values()],
        }
    
    def __contains__(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools
    
    def __getitem__(self, tool_name: str) -> Optional[ToolAdapter]:
        """Get adapter for a tool name (dict-like access)."""
        return self.get_adapter_for_tool(tool_name)


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def register_adapter(name: str, adapter: ToolAdapter) -> None:
    """Register an adapter with the global registry.
    
    Convenience function for get_registry().register_adapter().
    """
    get_registry().register_adapter(name, adapter)


def get_tool(tool_name: str) -> Optional[Tool]:
    """Get a tool from the global registry.
    
    Convenience function for get_registry().get_tool().
    """
    return get_registry().get_tool(tool_name)


def list_tools(
    capability: Optional[ToolCapability] = None,
    tag: Optional[str] = None,
) -> List[Tool]:
    """List tools from the global registry.
    
    Convenience function for get_registry().list_tools().
    """
    return get_registry().list_tools(capability=capability, tag=tag)
