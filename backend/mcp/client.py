"""MCP Client Interface.

Provides a unified interface for invoking tools through the registry.
Handles input validation, invocation, and result processing.
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from mcp.types import (
    Tool,
    ToolInput,
    ToolResult,
    ToolError,
    ToolErrorCode,
    ToolInvocation,
)
from mcp.registry import ToolRegistry, get_registry

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP Client for tool invocation.
    
    Provides a unified interface for invoking tools with:
    - Input validation
    - Timeout handling
    - Error wrapping
    - Invocation logging
    """
    
    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        default_timeout: int = 30,
        enable_logging: bool = True,
    ):
        """Initialize the MCP client.
        
        Args:
            registry: Tool registry to use (defaults to global registry)
            default_timeout: Default timeout for tool invocations in seconds
            enable_logging: Whether to log invocations
        """
        self._registry = registry or get_registry()
        self._default_timeout = default_timeout
        self._enable_logging = enable_logging
        self._invocation_log: List[ToolInvocation] = []
    
    async def invoke(
        self,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Any] = None,
        timeout: Optional[int] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> ToolResult:
        """Invoke a tool by name.
        
        Args:
            tool_name: The full tool name (e.g., "market_data.fetch_assets")
            parameters: Input parameters for the tool
            context: Optional context (task state, session, etc.)
            timeout: Override default timeout
            user_id: User ID for audit logging
            session_id: Session ID for audit logging
            task_id: Task ID for audit logging
        
        Returns:
            ToolResult with success/failure and data/error
        """
        invocation_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc)
        start_time = time.time()
        
        # Create invocation record
        tool_input = ToolInput(
            tool_name=tool_name,
            parameters=parameters or {},
            context=context,
        )
        
        invocation = ToolInvocation(
            invocation_id=invocation_id,
            tool_name=tool_name,
            input=tool_input,
            user_id=user_id,
            session_id=session_id,
            task_id=task_id,
            started_at=started_at,
        )
        
        try:
            # Get tool definition
            tool = self._registry.get_tool(tool_name)
            if not tool:
                raise ToolError(
                    f"Tool not found: {tool_name}",
                    code=ToolErrorCode.NOT_FOUND,
                )
            
            # Get adapter
            adapter = self._registry.get_adapter_for_tool(tool_name)
            if not adapter:
                raise ToolError(
                    f"No adapter found for tool: {tool_name}",
                    code=ToolErrorCode.NOT_FOUND,
                )
            
            # Validate input
            self._validate_input(tool, parameters or {})
            
            # Extract method name from tool name
            # e.g., "market_data.fetch_assets" -> "fetch_assets"
            method_name = tool_name.split(".", 1)[1] if "." in tool_name else tool_name
            
            # Invoke with timeout
            effective_timeout = timeout or tool.timeout_seconds or self._default_timeout
            
            try:
                raw_result = await asyncio.wait_for(
                    adapter.invoke(method_name, parameters or {}, context),
                    timeout=effective_timeout,
                )
            except asyncio.TimeoutError:
                raise ToolError(
                    f"Tool invocation timed out after {effective_timeout}s",
                    code=ToolErrorCode.TIMEOUT,
                )
            
            # Process result
            duration_ms = int((time.time() - start_time) * 1000)
            
            if isinstance(raw_result, ToolResult):
                result = raw_result
                result.duration_ms = duration_ms
            else:
                result = ToolResult(
                    success=True,
                    data=raw_result.get("data") if isinstance(raw_result, dict) else raw_result,
                    metadata=raw_result.get("metadata") if isinstance(raw_result, dict) else None,
                    duration_ms=duration_ms,
                )
            
        except ToolError as e:
            result = e.to_result()
            result.duration_ms = int((time.time() - start_time) * 1000)
        except Exception as e:
            logger.error(f"Tool invocation failed: {e}")
            result = ToolResult(
                success=False,
                error=str(e),
                error_code=ToolErrorCode.INTERNAL_ERROR.value,
                duration_ms=int((time.time() - start_time) * 1000),
            )
        
        # Complete invocation record
        invocation.result = result
        invocation.completed_at = datetime.now(timezone.utc)
        
        if self._enable_logging:
            self._invocation_log.append(invocation)
            if len(self._invocation_log) > 1000:
                # Keep only last 1000 invocations in memory
                self._invocation_log = self._invocation_log[-500:]
        
        logger.debug(
            f"Tool invocation: {tool_name} "
            f"success={result.success} "
            f"duration={result.duration_ms}ms"
        )
        
        return result
    
    def _validate_input(self, tool: Tool, parameters: Dict[str, Any]) -> None:
        """Validate input parameters against tool schema.
        
        Raises:
            ToolError: If validation fails
        """
        # Check required parameters
        required = [p.name for p in tool.parameters if p.required]
        missing = [name for name in required if name not in parameters]
        
        if missing:
            raise ToolError(
                f"Missing required parameters: {', '.join(missing)}",
                code=ToolErrorCode.INVALID_INPUT,
                details={"missing": missing},
            )
        
        # Type validation could be added here
    
    async def invoke_many(
        self,
        invocations: List[Dict[str, Any]],
        parallel: bool = True,
    ) -> List[ToolResult]:
        """Invoke multiple tools.
        
        Args:
            invocations: List of invocation dicts with tool_name and parameters
            parallel: If True, invoke all tools in parallel
        
        Returns:
            List of ToolResults in the same order
        """
        if parallel:
            tasks = [
                self.invoke(
                    tool_name=inv.get("tool_name", ""),
                    parameters=inv.get("parameters", {}),
                    context=inv.get("context"),
                    user_id=inv.get("user_id"),
                    session_id=inv.get("session_id"),
                    task_id=inv.get("task_id"),
                )
                for inv in invocations
            ]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for inv in invocations:
                result = await self.invoke(
                    tool_name=inv.get("tool_name", ""),
                    parameters=inv.get("parameters", {}),
                    context=inv.get("context"),
                    user_id=inv.get("user_id"),
                    session_id=inv.get("session_id"),
                    task_id=inv.get("task_id"),
                )
                results.append(result)
            return results
    
    def get_invocation_log(
        self,
        limit: int = 100,
        tool_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[ToolInvocation]:
        """Get recent invocation log.
        
        Args:
            limit: Maximum number of invocations to return
            tool_name: Filter by tool name
            user_id: Filter by user ID
        
        Returns:
            List of recent invocations (newest first)
        """
        log = self._invocation_log[::-1]  # Reverse to newest first
        
        if tool_name:
            log = [inv for inv in log if inv.tool_name == tool_name]
        
        if user_id:
            log = [inv for inv in log if inv.user_id == user_id]
        
        return log[:limit]
    
    def clear_invocation_log(self) -> None:
        """Clear the invocation log."""
        self._invocation_log.clear()
    
    def list_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return self._registry.list_tool_names()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool information.
        
        Args:
            tool_name: The tool name
        
        Returns:
            Tool info dict or None if not found
        """
        tool = self._registry.get_tool(tool_name)
        return tool.to_dict() if tool else None


# Global client instance
_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get the global MCP client."""
    global _client
    if _client is None:
        _client = MCPClient()
    return _client


def init_mcp_client(
    registry: Optional[ToolRegistry] = None,
    default_timeout: int = 30,
    enable_logging: bool = True,
) -> MCPClient:
    """Initialize the global MCP client.
    
    Args:
        registry: Tool registry to use
        default_timeout: Default timeout for invocations
        enable_logging: Whether to log invocations
    
    Returns:
        The initialized MCP client
    """
    global _client
    _client = MCPClient(
        registry=registry,
        default_timeout=default_timeout,
        enable_logging=enable_logging,
    )
    return _client


async def invoke_tool(
    tool_name: str,
    parameters: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> ToolResult:
    """Convenience function to invoke a tool.
    
    Uses the global MCP client.
    """
    return await get_mcp_client().invoke(tool_name, parameters, **kwargs)
