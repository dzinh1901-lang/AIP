"""Analytics Adapter.

Wraps agents/analytics.py for MCP-compatible access to analytics and KPI reporting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class AnalyticsAdapter:
    """Adapter for analytics services.
    
    Wraps:
    - generate_kpi_report
    - run_anomaly_check
    - check_anomalies_from_metrics
    - get_recent_activities
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for analytics."""
        return [
            Tool(
                name="analytics.generate_kpi",
                description="Generate a KPI report with platform metrics, signal health, and user engagement",
                capability=ToolCapability.GENERATE,
                parameters=[],
                requires_approval=False,
                timeout_seconds=45,
                rate_limit=10,
                tags=["analytics", "kpi", "metrics", "reports"],
            ),
            Tool(
                name="analytics.get_kpi",
                description="Get the latest KPI report",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=10,
                tags=["analytics", "kpi", "metrics"],
            ),
            Tool(
                name="analytics.check_anomalies",
                description="Run anomaly detection on current platform data to identify unusual patterns",
                capability=ToolCapability.ANALYZE,
                parameters=[],
                requires_approval=False,
                timeout_seconds=30,
                tags=["analytics", "anomaly", "detection"],
            ),
            Tool(
                name="analytics.check_custom_metrics",
                description="Check custom metrics for anomalies",
                capability=ToolCapability.ANALYZE,
                parameters=[
                    ToolParameter(
                        name="metrics",
                        param_type="object",
                        description="Dictionary of metric names to values",
                        required=True,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=30,
                tags=["analytics", "anomaly", "custom"],
            ),
            Tool(
                name="analytics.get_activity",
                description="Get recent agent activity log",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="limit",
                        param_type="number",
                        description="Number of activities to retrieve",
                        required=False,
                        default=50,
                    ),
                    ToolParameter(
                        name="agent_name",
                        param_type="string",
                        description="Filter by agent name",
                        required=False,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["analytics", "activity", "logs"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke an analytics method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        import agents.analytics as analytics_agent
        
        # Build state from context or fetch fresh
        state = await self._get_state(context)
        
        if method == "generate_kpi":
            report = await analytics_agent.generate_kpi_report(state)
            return {
                "data": {"report": report},
                "metadata": {"generated": True},
            }
        
        elif method == "get_kpi":
            report = await analytics_agent.get_latest_kpi_report()
            return {
                "data": report,
            }
        
        elif method == "check_anomalies":
            result = await analytics_agent.run_anomaly_check(state)
            return {
                "data": {"analysis": result},
            }
        
        elif method == "check_custom_metrics":
            metrics = params.get("metrics", {})
            if not metrics:
                return {"data": None, "error": "metrics required"}
            
            result = await analytics_agent.check_anomalies_from_metrics(metrics)
            return {
                "data": {"analysis": result},
            }
        
        elif method == "get_activity":
            limit = params.get("limit", 50)
            agent_name = params.get("agent_name")
            
            activities = await analytics_agent.get_recent_activities(limit=limit)
            
            # Filter by agent if specified
            if agent_name:
                activities = [a for a in activities if a.get("agent_name") == agent_name]
            
            return {
                "data": activities,
                "metadata": {"count": len(activities)},
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _get_state(self, context: Optional[Any]) -> Dict[str, Any]:
        """Get current state for analytics."""
        # Try to use cached state from context
        if context and hasattr(context, "context") and context.context:
            return {
                "assets": context.context.get("assets", []),
                "consensus": context.context.get("consensus", []),
                "last_updated": context.context.get("last_updated"),
            }
        
        # Fetch fresh data
        from services.data_service import fetch_all_assets
        
        assets = await fetch_all_assets()
        return {
            "assets": assets,
            "consensus": [],  # Would need to compute
            "last_updated": None,
        }
