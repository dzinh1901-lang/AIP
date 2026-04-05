"""Marketing Adapter.

Wraps agents/marketing.py for MCP-compatible access to marketing content generation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class MarketingAdapter:
    """Adapter for marketing services.
    
    Wraps:
    - generate_daily_teaser
    - generate_lead_nurture
    - get_lead_insight
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for marketing."""
        return [
            Tool(
                name="marketing.generate_teaser",
                description="Generate a daily market teaser for social media/marketing",
                capability=ToolCapability.GENERATE,
                parameters=[],
                requires_approval=False,
                timeout_seconds=45,
                rate_limit=5,
                tags=["marketing", "content", "teaser"],
            ),
            Tool(
                name="marketing.generate_nurture",
                description="Generate lead nurture content",
                capability=ToolCapability.GENERATE,
                parameters=[],
                requires_approval=False,
                timeout_seconds=45,
                rate_limit=5,
                tags=["marketing", "content", "nurture"],
            ),
            Tool(
                name="marketing.lead_insight",
                description="Generate insights for a specific lead context",
                capability=ToolCapability.GENERATE,
                parameters=[
                    ToolParameter(
                        name="lead_context",
                        param_type="string",
                        description="Context about the lead (interests, needs, etc.)",
                        required=True,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=30,
                rate_limit=10,
                tags=["marketing", "leads", "insights"],
            ),
            Tool(
                name="marketing.get_content_history",
                description="Get historical marketing content",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="content_type",
                        param_type="string",
                        description="Filter by content type (teaser, nurture)",
                        required=False,
                    ),
                    ToolParameter(
                        name="limit",
                        param_type="number",
                        description="Number of items to retrieve",
                        required=False,
                        default=10,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["marketing", "content", "history"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a marketing method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        import agents.marketing as mkt_agent
        
        # Build state from context or fetch fresh
        state = await self._get_state(context)
        
        if method == "generate_teaser":
            content = await mkt_agent.generate_daily_teaser(state)
            
            return {
                "data": {"content": content, "type": "teaser"},
                "metadata": {"generated": True},
            }
        
        elif method == "generate_nurture":
            content = await mkt_agent.generate_lead_nurture(state)
            
            return {
                "data": {"content": content, "type": "nurture"},
                "metadata": {"generated": True},
            }
        
        elif method == "lead_insight":
            lead_context = params.get("lead_context", "")
            if not lead_context:
                return {"data": None, "error": "lead_context required"}
            
            # Sanitize input
            from security import sanitize_input
            try:
                lead_context = sanitize_input(lead_context)
            except ValueError as e:
                return {"data": None, "error": str(e)}
            
            insight = await mkt_agent.get_lead_insight(lead_context, state)
            
            return {
                "data": {"insight": insight},
            }
        
        elif method == "get_content_history":
            content_type = params.get("content_type")
            limit = params.get("limit", 10)
            
            from db import get_db
            
            query = "SELECT * FROM marketing_content ORDER BY timestamp DESC LIMIT ?"
            query_params = [limit]
            
            async with get_db() as db:
                rows = await db.fetchall(query, query_params)
            
            content = [
                {
                    "id": r["id"],
                    "content_type": r["content_type"],
                    "title": r.get("title"),
                    "content": r["content"],
                    "timestamp": r.get("timestamp"),
                }
                for r in rows
            ]
            
            # Filter by type if specified
            if content_type:
                content = [c for c in content if c["content_type"] == content_type]
            
            return {
                "data": content,
                "metadata": {"count": len(content)},
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _get_state(self, context: Optional[Any]) -> Dict[str, Any]:
        """Get current state for marketing."""
        from services.data_service import fetch_all_assets
        
        assets = await fetch_all_assets()
        return {
            "assets": assets,
            "consensus": [],
        }
