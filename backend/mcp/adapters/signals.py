"""Signals Adapter.

Wraps services/signal_engine.py for MCP-compatible access to signal generation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class SignalsAdapter:
    """Adapter for signal generation services.
    
    Wraps:
    - generate_all_signals
    - generate_signal
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for signals."""
        return [
            Tool(
                name="signals.generate_signals",
                description="Generate trading signals for all tracked assets based on price action and macro context",
                capability=ToolCapability.ANALYZE,
                parameters=[],
                requires_approval=False,
                timeout_seconds=30,
                tags=["signals", "analysis", "trading"],
            ),
            Tool(
                name="signals.generate_signal",
                description="Generate a trading signal for a specific asset",
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
                timeout_seconds=15,
                tags=["signals", "analysis", "trading"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a signal generation method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        from services.signal_engine import generate_all_signals, generate_signal
        from services.data_service import fetch_all_assets, fetch_macro_context
        
        if method == "generate_signals":
            # Fetch current data
            assets = await fetch_all_assets()
            macro_context = await fetch_macro_context()
            
            # Generate signals
            signals = generate_all_signals(assets, macro_context)
            
            return {
                "data": [s.model_dump() for s in signals],
                "metadata": {"count": len(signals)},
            }
        
        elif method == "generate_signal":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"data": None, "error": "Symbol required"}
            
            # Fetch current data
            assets = await fetch_all_assets()
            macro_context = await fetch_macro_context()
            
            # Find the asset
            asset = next((a for a in assets if a.symbol == symbol), None)
            if not asset:
                return {"data": None, "error": f"Asset not found: {symbol}"}
            
            # Generate signal
            signal = generate_signal(asset, macro_context)
            
            return {"data": signal.model_dump()}
        
        else:
            raise ValueError(f"Unknown method: {method}")
