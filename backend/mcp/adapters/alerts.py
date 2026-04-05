"""Alerts Adapter.

Wraps services/alert_engine.py for MCP-compatible access to alerts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class AlertsAdapter:
    """Adapter for alert services.
    
    Wraps:
    - get_recent_alerts
    - mark_alert_read
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for alerts."""
        return [
            Tool(
                name="alerts.get_recent",
                description="Get recent alerts for all assets or a specific asset",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="symbol",
                        param_type="string",
                        description="Filter by asset symbol (optional)",
                        required=False,
                    ),
                    ToolParameter(
                        name="limit",
                        param_type="number",
                        description="Maximum number of alerts to return",
                        required=False,
                        default=20,
                    ),
                    ToolParameter(
                        name="unread_only",
                        param_type="boolean",
                        description="Only return unread alerts",
                        required=False,
                        default=False,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["alerts", "notifications"],
            ),
            Tool(
                name="alerts.mark_read",
                description="Mark an alert as read",
                capability=ToolCapability.WRITE,
                parameters=[
                    ToolParameter(
                        name="alert_id",
                        param_type="number",
                        description="The alert ID to mark as read",
                        required=True,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=5,
                tags=["alerts", "notifications"],
            ),
            Tool(
                name="alerts.get_by_severity",
                description="Get alerts filtered by severity level",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="severity",
                        param_type="string",
                        description="Severity level: info, warning, critical",
                        required=True,
                        enum=["info", "warning", "critical"],
                    ),
                    ToolParameter(
                        name="limit",
                        param_type="number",
                        description="Maximum number of alerts",
                        required=False,
                        default=20,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["alerts", "notifications", "severity"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke an alert method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        from services.alert_engine import get_recent_alerts, mark_alert_read
        
        if method == "get_recent":
            limit = params.get("limit", 20)
            symbol = params.get("symbol")
            unread_only = params.get("unread_only", False)
            
            alerts = await get_recent_alerts(limit=limit)
            
            # Filter by symbol if specified
            if symbol:
                symbol = symbol.upper()
                alerts = [a for a in alerts if a.get("asset") == symbol]
            
            # Filter unread if specified
            if unread_only:
                alerts = [a for a in alerts if not a.get("is_read", False)]
            
            return {
                "data": alerts,
                "metadata": {"count": len(alerts)},
            }
        
        elif method == "mark_read":
            alert_id = params.get("alert_id")
            if not alert_id:
                return {"data": None, "error": "alert_id required"}
            
            success = await mark_alert_read(alert_id)
            
            return {
                "data": {"success": success, "alert_id": alert_id},
            }
        
        elif method == "get_by_severity":
            severity = params.get("severity", "").lower()
            limit = params.get("limit", 20)
            
            if severity not in ("info", "warning", "critical"):
                return {"data": None, "error": "Invalid severity level"}
            
            alerts = await get_recent_alerts(limit=limit * 2)  # Get more to filter
            alerts = [a for a in alerts if a.get("severity") == severity][:limit]
            
            return {
                "data": alerts,
                "metadata": {"count": len(alerts), "severity": severity},
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
