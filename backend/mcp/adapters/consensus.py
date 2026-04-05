"""Consensus Adapter.

Wraps services/consensus_engine.py and services/model_wrapper.py for 
MCP-compatible access to AI model consensus.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class ConsensusAdapter:
    """Adapter for consensus and AI model services.
    
    Wraps:
    - compute_consensus
    - query_all_models
    - debate_loop
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for consensus."""
        return [
            Tool(
                name="consensus.get_consensus",
                description="Get the latest AI model consensus results for all tracked assets",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=10,
                tags=["consensus", "ai", "models"],
            ),
            Tool(
                name="consensus.compute_consensus",
                description="Compute fresh AI consensus for a specific asset using all models",
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
                rate_limit=10,
                tags=["consensus", "ai", "models", "compute"],
            ),
            Tool(
                name="consensus.run_debate",
                description="Run AI debate loop where models refine their positions considering other model outputs",
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
                timeout_seconds=90,
                rate_limit=5,
                tags=["consensus", "ai", "models", "debate"],
            ),
            Tool(
                name="consensus.get_model_outputs",
                description="Get individual AI model outputs for a specific asset",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="symbol",
                        param_type="string",
                        description="Asset symbol",
                        required=False,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["consensus", "ai", "models"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a consensus method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context (includes shared state)
        
        Returns:
            Dict with "data" key containing results
        """
        from services.consensus_engine import compute_consensus
        from services.model_wrapper import query_all_models, debate_loop
        from services.signal_engine import generate_signal
        from services.learning_engine import get_model_weights
        from services.data_service import fetch_all_assets, fetch_macro_context
        
        if method == "get_consensus":
            # Return cached consensus from context if available
            if context and hasattr(context, "context") and context.context:
                cached = context.context.get("consensus", [])
                if cached:
                    return {
                        "data": [c.model_dump() if hasattr(c, "model_dump") else c for c in cached],
                        "metadata": {"source": "cached"},
                    }
            
            # Otherwise fetch fresh
            return await self._compute_all_consensus()
        
        elif method == "compute_consensus":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"data": None, "error": "Symbol required"}
            
            return await self._compute_consensus_for_symbol(symbol)
        
        elif method == "run_debate":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"data": None, "error": "Symbol required"}
            
            return await self._run_debate_for_symbol(symbol)
        
        elif method == "get_model_outputs":
            symbol = params.get("symbol", "").upper() if params.get("symbol") else None
            
            # Get from database
            from db import get_db
            
            async with get_db() as db:
                if symbol:
                    rows = await db.fetchall(
                        "SELECT * FROM model_outputs WHERE asset = ? ORDER BY timestamp DESC LIMIT 10",
                        (symbol,),
                    )
                else:
                    rows = await db.fetchall(
                        "SELECT * FROM model_outputs ORDER BY timestamp DESC LIMIT 30",
                    )
            
            import json
            outputs = [
                {
                    "asset": r["asset"],
                    "model_name": r["model_name"],
                    "signal": r["signal"],
                    "confidence": r["confidence"],
                    "reasoning": json.loads(r["reasoning"]) if r.get("reasoning") else [],
                    "timestamp": r.get("timestamp"),
                }
                for r in rows
            ]
            
            return {"data": outputs}
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _compute_all_consensus(self) -> Dict[str, Any]:
        """Compute consensus for all assets."""
        from services.consensus_engine import compute_consensus
        from services.model_wrapper import query_all_models, debate_loop
        from services.signal_engine import generate_all_signals
        from services.learning_engine import get_model_weights
        from services.data_service import fetch_all_assets, fetch_macro_context
        
        assets = await fetch_all_assets()
        macro = await fetch_macro_context()
        signals = generate_all_signals(assets, macro)
        
        all_consensus = []
        for signal in signals:
            weights = await get_model_weights(signal.asset)
            outputs = await query_all_models(signal, macro)
            refined = await debate_loop(signal, macro, outputs)
            consensus = compute_consensus(signal.asset, refined, weights)
            all_consensus.append(consensus.model_dump())
        
        return {
            "data": all_consensus,
            "metadata": {"count": len(all_consensus)},
        }
    
    async def _compute_consensus_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Compute consensus for a specific symbol."""
        from services.consensus_engine import compute_consensus
        from services.model_wrapper import query_all_models
        from services.signal_engine import generate_signal
        from services.learning_engine import get_model_weights
        from services.data_service import fetch_all_assets, fetch_macro_context
        
        assets = await fetch_all_assets()
        macro = await fetch_macro_context()
        
        asset = next((a for a in assets if a.symbol == symbol), None)
        if not asset:
            return {"data": None, "error": f"Asset not found: {symbol}"}
        
        signal = generate_signal(asset, macro)
        weights = await get_model_weights(symbol)
        outputs = await query_all_models(signal, macro)
        consensus = compute_consensus(symbol, outputs, weights)
        
        return {"data": consensus.model_dump()}
    
    async def _run_debate_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Run full debate loop for a specific symbol."""
        from services.consensus_engine import compute_consensus
        from services.model_wrapper import query_all_models, debate_loop
        from services.signal_engine import generate_signal
        from services.learning_engine import get_model_weights
        from services.data_service import fetch_all_assets, fetch_macro_context
        
        assets = await fetch_all_assets()
        macro = await fetch_macro_context()
        
        asset = next((a for a in assets if a.symbol == symbol), None)
        if not asset:
            return {"data": None, "error": f"Asset not found: {symbol}"}
        
        signal = generate_signal(asset, macro)
        weights = await get_model_weights(symbol)
        initial_outputs = await query_all_models(signal, macro)
        refined_outputs = await debate_loop(signal, macro, initial_outputs)
        consensus = compute_consensus(symbol, refined_outputs, weights)
        
        return {
            "data": {
                "consensus": consensus.model_dump(),
                "initial_outputs": [o.model_dump() for o in initial_outputs],
                "refined_outputs": [o.model_dump() for o in refined_outputs],
            },
            "metadata": {"debate_rounds": 1},
        }
