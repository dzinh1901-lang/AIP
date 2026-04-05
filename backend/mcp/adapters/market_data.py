"""Market Data Adapter.

Wraps services/data_service.py for MCP-compatible access to market data.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter, ToolResult


class MarketDataAdapter:
    """Adapter for market data services.
    
    Wraps:
    - fetch_all_assets
    - fetch_crypto_prices
    - fetch_commodity_prices
    - fetch_macro_context
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for market data."""
        return [
            Tool(
                name="market_data.fetch_assets",
                description="Fetch current prices for all tracked crypto and commodity assets including BTC, ETH, Gold, Oil",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=30,
                tags=["market", "prices", "assets", "crypto", "commodity"],
            ),
            Tool(
                name="market_data.fetch_crypto",
                description="Fetch current prices for cryptocurrency assets only",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=20,
                tags=["market", "prices", "crypto"],
            ),
            Tool(
                name="market_data.fetch_commodities",
                description="Fetch current prices for commodity assets only (Gold, Oil)",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=20,
                tags=["market", "prices", "commodity"],
            ),
            Tool(
                name="market_data.fetch_macro_context",
                description="Fetch macro market context including USD index, 10Y bond yield, VIX, news sentiment, and on-chain activity",
                capability=ToolCapability.READ,
                parameters=[],
                requires_approval=False,
                timeout_seconds=30,
                tags=["market", "macro", "context", "sentiment"],
            ),
            Tool(
                name="market_data.get_asset_price",
                description="Get the current price for a specific asset by symbol",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="symbol",
                        param_type="string",
                        description="Asset symbol (e.g., BTC, ETH, GOLD, OIL)",
                        required=True,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=15,
                tags=["market", "prices", "asset"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a market data method.
        
        Args:
            method: The method name (fetch_assets, fetch_crypto, etc.)
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        from services.data_service import (
            fetch_all_assets,
            fetch_crypto_prices,
            fetch_commodity_prices,
            fetch_macro_context,
        )
        
        if method == "fetch_assets":
            assets = await fetch_all_assets()
            return {
                "data": [a.model_dump() for a in assets],
                "metadata": {"count": len(assets)},
            }
        
        elif method == "fetch_crypto":
            assets = await fetch_crypto_prices()
            return {
                "data": [a.model_dump() for a in assets],
                "metadata": {"count": len(assets)},
            }
        
        elif method == "fetch_commodities":
            assets = await fetch_commodity_prices()
            return {
                "data": [a.model_dump() for a in assets],
                "metadata": {"count": len(assets)},
            }
        
        elif method == "fetch_macro_context":
            context_data = await fetch_macro_context()
            return {
                "data": context_data.model_dump(),
            }
        
        elif method == "get_asset_price":
            symbol = params.get("symbol", "").upper()
            if not symbol:
                return {"data": None, "error": "Symbol required"}
            
            assets = await fetch_all_assets()
            asset = next((a for a in assets if a.symbol == symbol), None)
            
            if asset:
                return {"data": asset.model_dump()}
            else:
                return {"data": None, "error": f"Asset not found: {symbol}"}
        
        else:
            raise ValueError(f"Unknown method: {method}")
