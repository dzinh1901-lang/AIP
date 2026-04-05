"""Market Intelligence Adapter.

Wraps agents/market_intelligence.py for MCP-compatible access to 
market narratives and deep-dive analysis.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class MarketIntelAdapter:
    """Adapter for market intelligence services.
    
    Wraps:
    - generate_narrative
    - deep_dive
    - get_latest_narrative
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for market intelligence."""
        return [
            Tool(
                name="market_intel.get_narrative",
                description="Get the latest market narrative report",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=10,
                tags=["market", "narrative", "analysis"],
            ),
            Tool(
                name="market_intel.generate_narrative",
                description="Generate a market narrative report (pre-market or close summary)",
                capability=ToolCapability.GENERATE,
                parameters=[
                    ToolParameter(
                        name="report_type",
                        param_type="string",
                        description="Type of report: pre_market or close_summary",
                        required=False,
                        default="pre_market",
                        enum=["pre_market", "close_summary"],
                    ),
                ],
                requires_approval=False,
                timeout_seconds=60,
                rate_limit=10,
                tags=["market", "narrative", "analysis", "generate"],
            ),
            Tool(
                name="market_intel.deep_dive",
                description="Generate a detailed deep-dive analysis for a specific asset",
                capability=ToolCapability.ANALYZE,
                parameters=[
                    ToolParameter(
                        name="symbol",
                        param_type="string",
                        description="Asset symbol (e.g., BTC, ETH, GOLD)",
                        required=True,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=60,
                rate_limit=20,
                tags=["market", "analysis", "deep-dive", "asset"],
            ),
            Tool(
                name="market_intel.get_report_history",
                description="Get historical market intelligence reports",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="limit",
                        param_type="number",
                        description="Number of reports to retrieve",
                        required=False,
                        default=10,
                    ),
                    ToolParameter(
                        name="report_type",
                        param_type="string",
                        description="Filter by report type",
                        required=False,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["market", "narrative", "history"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a market intelligence method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        import agents.market_intelligence as intel_agent
        
        # Build state from context or fetch fresh
        state = await self._get_state(context)
        
        if method == "get_narrative":
            narrative = await intel_agent.get_latest_narrative()
            return {
                "data": narrative,
            }
        
        elif method == "generate_narrative":
            report_type = params.get("report_type", "pre_market")
            
            if report_type not in ("pre_market", "close_summary"):
                return {"data": None, "error": "Invalid report type"}
            
            content = await intel_agent.generate_narrative(report_type, state)
            
            return {
                "data": {"content": content, "type": report_type},
                "metadata": {"generated": True},
            }
        
        elif method == "deep_dive":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"data": None, "error": "Symbol required"}
            
            analysis = await intel_agent.deep_dive(symbol, state)
            
            return {
                "data": {"analysis": analysis, "symbol": symbol},
                "metadata": {"generated": True},
            }
        
        elif method == "get_report_history":
            limit = params.get("limit", 10)
            report_type = params.get("report_type")
            
            from db import get_db
            import json
            
            query = "SELECT * FROM market_intel_reports ORDER BY timestamp DESC LIMIT ?"
            query_params = [limit]
            
            async with get_db() as db:
                rows = await db.fetchall(query, query_params)
            
            reports = [
                {
                    "id": r["id"],
                    "report_type": r["report_type"],
                    "content": r["content"],
                    "assets_covered": json.loads(r["assets_covered"]) if r.get("assets_covered") else [],
                    "date": r.get("date"),
                    "timestamp": r.get("timestamp"),
                }
                for r in rows
            ]
            
            # Filter by type if specified
            if report_type:
                reports = [r for r in reports if r["report_type"] == report_type]
            
            return {
                "data": reports,
                "metadata": {"count": len(reports)},
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _get_state(self, context: Optional[Any]) -> Dict[str, Any]:
        """Get current state for market intelligence."""
        from services.data_service import fetch_all_assets, fetch_macro_context
        from services.signal_engine import generate_all_signals
        from services.consensus_engine import compute_consensus
        from services.model_wrapper import query_all_models
        from services.learning_engine import get_model_weights
        
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
        }
