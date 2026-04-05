"""Coordinator API Routes.

FastAPI routes for the coordinator service including:
- Chat endpoint with SSE streaming
- Task management endpoints
- Session management endpoints
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from auth import get_optional_user, require_auth, User
from coordinator.engine import get_coordinator, CoordinatorEngine
from coordinator.models import (
    TaskState,
    TaskStatus,
    SessionContext,
    FinalResponse,
)
from coordinator.session import SessionManager, get_or_create_session
from coordinator.streaming import (
    SSEFormatter,
    stream_coordinator_run,
    stream_task_events,
)
from security import sanitize_input

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/coordinator", tags=["coordinator"])


# ---------------------------------------------------------------------------
# Request/Response Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Request body for coordinator chat."""
    message: str
    session_id: Optional[str] = None
    prior_task_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response body for non-streaming chat."""
    answer: str
    task_id: str
    artifacts: List[Dict[str, Any]] = []
    evidence: List[str] = []
    step_summary: List[Dict[str, Any]] = []


class TaskResponse(BaseModel):
    """Response body for task queries."""
    task_id: str
    session_id: str
    goal: str
    status: str
    classification: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Request body for task approval."""
    approved: bool
    reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

async def get_session_context(
    request: Request,
    user: Optional[User] = None,
    session_id: Optional[str] = None,
) -> SessionContext:
    """Build session context from request and user."""
    if user:
        return await get_or_create_session(
            session_id=session_id,
            user={
                "id": str(user.id) if hasattr(user, 'id') else user.get("id", "anonymous"),
                "username": user.username if hasattr(user, 'username') else user.get("username", "anonymous"),
                "role": user.role if hasattr(user, 'role') else user.get("role", "readonly"),
            },
        )
    else:
        # Anonymous user
        return await get_or_create_session(
            session_id=session_id,
            user={
                "id": "anonymous",
                "username": "anonymous",
                "role": "readonly",
            },
        )


def get_engine() -> CoordinatorEngine:
    """Get the coordinator engine (dependency injection)."""
    return get_coordinator()


# ---------------------------------------------------------------------------
# Chat Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: Optional[User] = Depends(get_optional_user),
    engine: CoordinatorEngine = Depends(get_engine),
):
    """Process a chat message through the coordinator.
    
    Returns a complete response (non-streaming).
    For streaming, use /chat/stream endpoint.
    """
    # Build session context
    session_ctx = await get_session_context(
        request=None,
        user=user,
        session_id=request.session_id,
    )
    
    # Run coordinator
    try:
        response = await engine.run(
            session_context=session_ctx,
            user_message=request.message,
            prior_task_id=request.prior_task_id,
        )
    except Exception as e:
        logger.error(f"Coordinator error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    
    return ChatResponse(
        answer=response.answer,
        task_id=response.task_state.task_id if response.task_state else "",
        artifacts=[a.to_dict() for a in response.artifacts],
        evidence=response.evidence,
        step_summary=response.step_summary,
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user: Optional[User] = Depends(get_optional_user),
    engine: CoordinatorEngine = Depends(get_engine),
):
    """Process a chat message with SSE streaming.
    
    Returns Server-Sent Events with task progress and final response.
    """
    # Build session context
    session_ctx = await get_session_context(
        request=None,
        user=user,
        session_id=request.session_id,
    )
    
    # Return streaming response
    return StreamingResponse(
        stream_coordinator_run(
            coordinator=engine,
            session_context=session_ctx,
            user_message=request.message,
            prior_task_id=request.prior_task_id,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


# ---------------------------------------------------------------------------
# Task Management Endpoints
# ---------------------------------------------------------------------------

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user: Optional[User] = Depends(get_optional_user),
    engine: CoordinatorEngine = Depends(get_engine),
):
    """Get task state by ID."""
    task = await engine.load_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    
    return TaskResponse(
        task_id=task.task_id,
        session_id=task.session_id,
        goal=task.goal,
        status=task.status.value,
        classification=task.classification.value if task.classification else None,
        created_at=task.created_at.isoformat() if task.created_at else None,
        updated_at=task.updated_at.isoformat() if task.updated_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.get("/tasks/{task_id}/steps")
async def get_task_steps(
    task_id: str,
    user: Optional[User] = Depends(get_optional_user),
    engine: CoordinatorEngine = Depends(get_engine),
):
    """Get all steps for a task."""
    task = await engine.load_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    
    return {
        "task_id": task_id,
        "steps": [step.to_dict() for step in task.plan],
    }


@router.get("/tasks/{task_id}/events")
async def get_task_events(
    task_id: str,
    limit: int = 100,
    user: Optional[User] = Depends(get_optional_user),
):
    """Get event history for a task (for replay)."""
    from db import get_db
    
    async with get_db() as db:
        rows = await db.fetchall(
            "SELECT * FROM task_events WHERE task_id = ? ORDER BY timestamp DESC LIMIT ?",
            (task_id, limit),
        )
    
    events = [
        {
            "event_id": r["id"],
            "task_id": r["task_id"],
            "event_type": r["event_type"],
            "payload": json.loads(r["payload_json"]) if r.get("payload_json") else None,
            "timestamp": r.get("timestamp"),
        }
        for r in reversed(rows)  # Chronological order
    ]
    
    return {
        "task_id": task_id,
        "events": events,
        "count": len(events),
    }


@router.get("/tasks/{task_id}/stream")
async def stream_task(
    task_id: str,
    user: Optional[User] = Depends(get_optional_user),
):
    """Stream events for an existing task.
    
    Useful for reconnecting to a running task.
    """
    return StreamingResponse(
        stream_task_events(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/tasks/{task_id}/approve")
async def approve_task(
    task_id: str,
    request: ApprovalRequest,
    user: User = Depends(require_auth),
    engine: CoordinatorEngine = Depends(get_engine),
):
    """Approve or reject a pending task."""
    task = await engine.approve_task(task_id, approved=request.approved)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    
    return {
        "task_id": task_id,
        "status": task.status.value,
        "approved": request.approved,
    }


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    user: User = Depends(require_auth),
    engine: CoordinatorEngine = Depends(get_engine),
):
    """Cancel a running task."""
    task = await engine.cancel_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task not found: {task_id}",
        )
    
    return {
        "task_id": task_id,
        "status": task.status.value,
        "cancelled": True,
    }


# ---------------------------------------------------------------------------
# Session Endpoints
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/tasks")
async def get_session_tasks(
    session_id: str,
    limit: int = 20,
    user: Optional[User] = Depends(get_optional_user),
):
    """List tasks in a session."""
    from db import get_db
    
    async with get_db() as db:
        rows = await db.fetchall(
            "SELECT * FROM tasks WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit),
        )
    
    tasks = [
        {
            "task_id": r["id"],
            "goal": r["goal"],
            "status": r["status"],
            "classification": r.get("classification"),
            "created_at": r.get("created_at"),
        }
        for r in rows
    ]
    
    return {
        "session_id": session_id,
        "tasks": tasks,
        "count": len(tasks),
    }


@router.post("/sessions")
async def create_session(
    user: Optional[User] = Depends(get_optional_user),
):
    """Create a new coordinator session."""
    session_ctx = await get_session_context(
        request=None,
        user=user,
        session_id=None,  # Force new session
    )
    
    return {
        "session_id": session_ctx.session_id,
        "user_id": session_ctx.user_id,
        "role": session_ctx.role,
    }


@router.delete("/sessions/{session_id}")
async def end_session(
    session_id: str,
    user: Optional[User] = Depends(get_optional_user),
):
    """End a coordinator session."""
    await SessionManager.end_session(session_id)
    
    return {
        "session_id": session_id,
        "ended": True,
    }


# ---------------------------------------------------------------------------
# Tool Discovery Endpoints
# ---------------------------------------------------------------------------

@router.get("/tools")
async def list_tools(
    user: Optional[User] = Depends(get_optional_user),
):
    """List all available tools."""
    from mcp.bootstrap import get_tool_definitions
    
    tools = get_tool_definitions()
    
    return {
        "tools": tools,
        "count": len(tools),
    }


@router.get("/tools/{tool_name}")
async def get_tool(
    tool_name: str,
    user: Optional[User] = Depends(get_optional_user),
):
    """Get tool definition by name."""
    from mcp.registry import get_registry
    
    tool = get_registry().get_tool(tool_name)
    
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool not found: {tool_name}",
        )
    
    return tool.to_dict()
