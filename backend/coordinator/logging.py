"""Structured Logging for Coordinator.

Provides structured JSON logging for all coordinator events,
supporting observability and audit trail requirements.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from coordinator.models import TaskEvent, TaskEventType


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "tool_name"):
            log_data["tool_name"] = record.tool_name
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        return json.dumps(log_data)


class CoordinatorLogger:
    """Structured logger for coordinator operations."""
    
    def __init__(self, name: str = "coordinator"):
        self.logger = logging.getLogger(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup structured logging handlers."""
        # Only add handlers if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_task_event(self, event: TaskEvent):
        """Log a task event."""
        self.logger.info(
            f"Task event: {event.event_type.value}",
            extra={
                "task_id": event.task_id,
                "event_type": event.event_type.value,
            },
        )
    
    def log_tool_invocation(
        self,
        tool_name: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        success: bool = True,
        error: Optional[str] = None,
    ):
        """Log a tool invocation."""
        level = logging.INFO if success else logging.WARNING
        message = f"Tool invocation: {tool_name} {'succeeded' if success else 'failed'}"
        
        self.logger.log(
            level,
            message,
            extra={
                "tool_name": tool_name,
                "task_id": task_id,
                "session_id": session_id,
                "user_id": user_id,
                "duration_ms": duration_ms,
            },
        )
    
    def log_task_lifecycle(
        self,
        task_id: str,
        status: str,
        goal: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """Log task lifecycle changes."""
        self.logger.info(
            f"Task {status}: {goal[:50] if goal else 'unknown'}...",
            extra={
                "task_id": task_id,
                "session_id": session_id,
                "user_id": user_id,
                "event_type": f"task.{status}",
            },
        )
    
    def log_classification(
        self,
        task_id: str,
        classification_type: str,
        confidence: float,
    ):
        """Log request classification."""
        self.logger.info(
            f"Classified as {classification_type} (confidence: {confidence:.2f})",
            extra={
                "task_id": task_id,
                "event_type": "task.classified",
            },
        )
    
    def log_step_execution(
        self,
        task_id: str,
        step_id: str,
        description: str,
        tool: Optional[str] = None,
        success: bool = True,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Log step execution."""
        level = logging.INFO if success else logging.WARNING
        status = "completed" if success else "failed"
        
        self.logger.log(
            level,
            f"Step {status}: {description[:50]}...",
            extra={
                "task_id": task_id,
                "tool_name": tool,
                "duration_ms": duration_ms,
                "event_type": f"step.{status}",
            },
        )
    
    def log_error(
        self,
        message: str,
        task_id: Optional[str] = None,
        error: Optional[Exception] = None,
    ):
        """Log an error."""
        self.logger.error(
            message,
            extra={"task_id": task_id},
            exc_info=error is not None,
        )


# Global logger instance
_coordinator_logger: Optional[CoordinatorLogger] = None


def get_coordinator_logger() -> CoordinatorLogger:
    """Get the global coordinator logger."""
    global _coordinator_logger
    if _coordinator_logger is None:
        _coordinator_logger = CoordinatorLogger()
    return _coordinator_logger


def setup_structured_logging(
    level: int = logging.INFO,
    enable_json: bool = True,
):
    """Setup structured logging for the application.
    
    Args:
        level: Logging level
        enable_json: Whether to use JSON formatting
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add structured handler
    handler = logging.StreamHandler(sys.stdout)
    
    if enable_json:
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(levelname)s %(name)s: %(message)s")
        )
    
    root_logger.addHandler(handler)
    
    # Set coordinator logger
    global _coordinator_logger
    _coordinator_logger = CoordinatorLogger()
    
    logging.info("Structured logging configured")
