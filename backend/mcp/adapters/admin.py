"""Admin Adapter.

Wraps agents/orchestrator.py for MCP-compatible access to admin operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class AdminAdapter:
    """Adapter for admin/orchestrator services.
    
    Wraps:
    - handle_admin_query
    - get_latest_briefing
    - get_agent_statuses
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for admin."""
        return [
            Tool(
                name="admin.get_briefing",
                description="Get the latest admin operational briefing",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=10,
                tags=["admin", "briefing", "status"],
            ),
            Tool(
                name="admin.query",
                description="Ask the admin orchestrator any operational question",
                capability=ToolCapability.GENERATE,
                parameters=[
                    ToolParameter(
                        name="query",
                        param_type="string",
                        description="The operational question to ask",
                        required=True,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=45,
                rate_limit=30,
                tags=["admin", "query", "operations"],
            ),
            Tool(
                name="admin.get_agent_status",
                description="Get the current status of all platform agents",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=10,
                tags=["admin", "status", "agents"],
            ),
            Tool(
                name="admin.generate_briefing",
                description="Generate a fresh admin briefing",
                capability=ToolCapability.GENERATE,
                parameters=[],
                requires_approval=False,
                timeout_seconds=60,
                rate_limit=5,
                tags=["admin", "briefing", "generate"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke an admin method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        import agents.orchestrator as orch_agent
        
        # Build state from context or fetch fresh
        state = await self._get_state(context)
        
        if method == "get_briefing":
            briefing = await orch_agent.get_latest_briefing()
            return {
                "data": briefing,
            }
        
        elif method == "query":
            query = params.get("query", "")
            if not query:
                return {"data": None, "error": "Query required"}
            
            # Sanitize input
            from security import sanitize_input
            try:
                query = sanitize_input(query)
            except ValueError as e:
                return {"data": None, "error": str(e)}
            
            response = await orch_agent.handle_admin_query(query, state)
            
            return {
                "data": {"response": response},
            }
        
        elif method == "get_agent_status":
            statuses = await orch_agent._collect_agent_statuses(state)
            return {
                "data": statuses,
                "metadata": {"count": len(statuses)},
            }
        
        elif method == "generate_briefing":
            await orch_agent.run_daily_briefing(state)
            briefing = await orch_agent.get_latest_briefing()
            
            return {
                "data": briefing,
                "metadata": {"generated": True},
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _get_state(self, context: Optional[Any]) -> Dict[str, Any]:
        """Get current state for admin operations."""
        from services.data_service import fetch_all_assets, fetch_macro_context
        from services.signal_engine import generate_all_signals
        from services.consensus_engine import compute_consensus
        from services.model_wrapper import query_all_models
        from services.learning_engine import get_model_weights
        from datetime import datetime, timezone
        
        assets = await fetch_all_assets()
        macro = await fetch_macro_context()
        signals = generate_all_signals(assets, macro)
        
        # Build consensus
        all_consensus = []
        for signal in signals:
            weights = await get_model_weights(signal.asset)
            outputs = await query_all_models(signal, macro)
            consensus = compute_consensus(signal.asset, outputs, weights)
            all_consensus.append(consensus)
        
        return {
            "assets": assets,
            "context": macro,
            "signals": signals,
            "consensus": all_consensus,
            "last_updated": datetime.now(timezone.utc),
        }
