"""Support Adapter.

Wraps agents/customer_success.py for MCP-compatible access to support chat.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.types import Tool, ToolCapability, ToolParameter


class SupportAdapter:
    """Adapter for customer success/support services.
    
    Wraps:
    - chat
    - onboard
    """
    
    @staticmethod
    def get_tools() -> List[Tool]:
        """Get tool definitions for support."""
        return [
            Tool(
                name="support.chat",
                description="Send a message to the support chat assistant for help with the platform",
                capability=ToolCapability.GENERATE,
                parameters=[
                    ToolParameter(
                        name="message",
                        param_type="string",
                        description="The user's message or question",
                        required=True,
                    ),
                    ToolParameter(
                        name="session_id",
                        param_type="string",
                        description="Chat session ID for context continuity",
                        required=False,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=30,
                tags=["support", "chat", "help"],
            ),
            Tool(
                name="support.onboard",
                description="Get onboarding guidance for new users",
                capability=ToolCapability.GENERATE,
                parameters=[
                    ToolParameter(
                        name="name",
                        param_type="string",
                        description="User's name for personalization",
                        required=False,
                    ),
                    ToolParameter(
                        name="interest",
                        param_type="string",
                        description="User's area of interest (e.g., crypto, commodities)",
                        required=False,
                    ),
                    ToolParameter(
                        name="experience",
                        param_type="string",
                        description="User's experience level (beginner, intermediate, advanced)",
                        required=False,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=30,
                tags=["support", "onboarding", "help"],
            ),
            Tool(
                name="support.get_chat_history",
                description="Get chat history for a session",
                capability=ToolCapability.READ,
                parameters=[
                    ToolParameter(
                        name="session_id",
                        param_type="string",
                        description="Chat session ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="limit",
                        param_type="number",
                        description="Number of messages to retrieve",
                        required=False,
                        default=50,
                    ),
                ],
                requires_approval=False,
                timeout_seconds=10,
                tags=["support", "chat", "history"],
            ),
        ]
    
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Invoke a support method.
        
        Args:
            method: The method name
            params: Input parameters
            context: Optional task context
        
        Returns:
            Dict with "data" key containing results
        """
        import agents.customer_success as cs_agent
        
        if method == "chat":
            message = params.get("message", "")
            session_id = params.get("session_id")
            
            if not message:
                return {"data": None, "error": "Message required"}
            
            # Sanitize input
            from security import sanitize_input
            try:
                message = sanitize_input(message)
            except ValueError as e:
                return {"data": None, "error": str(e)}
            
            response = await cs_agent.handle_chat(message, session_id)
            
            return {
                "data": {"response": response, "session_id": session_id},
            }
        
        elif method == "onboard":
            name = params.get("name")
            interest = params.get("interest")
            experience = params.get("experience")
            
            response = await cs_agent.handle_onboard(
                name=name,
                interest=interest,
                experience=experience,
            )
            
            return {
                "data": {"response": response},
            }
        
        elif method == "get_chat_history":
            session_id = params.get("session_id")
            limit = params.get("limit", 50)
            
            if not session_id:
                return {"data": None, "error": "session_id required"}
            
            from db import get_db
            
            async with get_db() as db:
                rows = await db.fetchall(
                    "SELECT * FROM support_chats WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (session_id, limit),
                )
            
            messages = [
                {
                    "role": r["role"],
                    "message": r["message"],
                    "timestamp": r.get("timestamp"),
                }
                for r in reversed(rows)  # Chronological order
            ]
            
            return {
                "data": messages,
                "metadata": {"count": len(messages), "session_id": session_id},
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
