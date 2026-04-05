"""Briefs Adapter.

Wraps services/brief_generator.py for MCP-compatible access to market briefs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class BriefsAdapter:
    """Adapter for brief generation services.
    
    Wraps:
    - generate_brief
    - get_latest_brief
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for briefs."""
        return [
            Tool(
                name="briefs.get_latest",
                description="Get the latest market intelligence brief",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=10,
                tags=["briefs", "reports", "market"],
            ),
            Tool(
                name="briefs.generate",
                description="Generate a new market intelligence brief based on current data",
                capability=ToolCapability.GENERATE,
                parameters=[],
                requires_approval=False,
                timeout_seconds=60,
                rate_limit=5,
                tags=["briefs", "reports", "market", "generate"],
            ),
            Tool(
                name="briefs.get_history",
                description="Get historical briefs",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="limit",
                        param_type="number",
                        description="Number of briefs to retrieve",
                        required=False,
                        default=7,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["briefs", "reports", "history"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a brief method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        from services.brief_generator import generate_brief, get_latest_brief
        
        if method == "get_latest":
            brief = await get_latest_brief()
            
            if brief:
                return {"data": brief}
            else:
                return {"data": None, "metadata": {"message": "No brief available yet"}}
        
        elif method == "generate":
            # Need to fetch current data for brief generation
            from services.data_service import fetch_all_assets, fetch_macro_context
            from services.signal_engine import generate_all_signals
            from services.consensus_engine import compute_consensus
            from services.model_wrapper import query_all_models
            from services.learning_engine import get_model_weights
            
            assets = await fetch_all_assets()
            macro = await fetch_macro_context()
            signals = generate_all_signals(assets, macro)
            
            # Build consensus for brief
            all_consensus = []
            for signal in signals:
                weights = await get_model_weights(signal.asset)
                outputs = await query_all_models(signal, macro)
                consensus = compute_consensus(signal.asset, outputs, weights)
                all_consensus.append(consensus)
            
            # Generate brief
            brief = await generate_brief(assets, all_consensus)
            
            return {
                "data": brief,
                "metadata": {"generated": True},
            }
        
        elif method == "get_history":
            limit = params.get("limit", 7)
            
            from db import get_db
            import json
            
            async with get_db() as db:
                rows = await db.fetchall(
                    "SELECT * FROM briefs ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
            
            briefs = [
                {
                    "id": r["id"],
                    "content": r["content"],
                    "key_signals": json.loads(r["key_signals"]) if r.get("key_signals") else [],
                    "risks": json.loads(r["risks"]) if r.get("risks") else [],
                    "date": r.get("date"),
                    "timestamp": r.get("timestamp"),
                }
                for r in rows
            ]
            
            return {
                "data": briefs,
                "metadata": {"count": len(briefs)},
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
