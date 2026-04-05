"""MCP Type Definitions.

MCP-compatible type definitions for tool abstraction. These types provide
a standardized interface for defining, invoking, and handling tools.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ToolCapability(str, Enum):
    """Tool capability categories."""
    READ = "read"           # Read-only data retrieval
    WRITE = "write"         # Data modification
    GENERATE = "generate"   # AI-powered generation
    ANALYZE = "analyze"     # Analysis and insights
    EXECUTE = "execute"     # Action execution
    ADMIN = "admin"         # Administrative operations


@dataclass
class ToolParameter:
    """A parameter definition for a tool."""
    name: str
    param_type: str  # string, number, boolean, array, object
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        schema: Dict[str, Any] = {
            "type": self.param_type,
            "description": self.description,
        }
        if self.default is not None:
            schema["default"] = self.default
        if self.enum:
            schema["enum"] = self.enum
        return schema


@dataclass
class Tool:
    """MCP Tool definition.
    
    Represents a callable tool with metadata, input schema, and capabilities.
    """
    name: str
    description: str
    capability: ToolCapability
    parameters: List[ToolParameter] = field(default_factory=list)
    requires_approval: bool = False
    rate_limit: Optional[int] = None  # calls per minute
    timeout_seconds: int = 30
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "capability": self.capability.value,
            "parameters": {p.name: p.to_schema() for p in self.parameters},
            "required_parameters": [p.name for p in self.parameters if p.required],
            "requires_approval": self.requires_approval,
            "rate_limit": self.rate_limit,
            "timeout_seconds": self.timeout_seconds,
            "tags": self.tags,
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get JSON Schema for tool input."""
        properties = {}
        required = []
        
        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


@dataclass
class ToolInput:
    """Input to a tool invocation."""
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self.parameters.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "context": self.context,
        }


@dataclass
class ToolResult:
    """Result of a tool invocation."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
    
    @classmethod
    def success_result(
        cls,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Create a successful result."""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def error_result(
        cls,
        error: str,
        error_code: Optional[str] = None,
    ) -> ToolResult:
        """Create an error result."""
        return cls(success=False, error=error, error_code=error_code)


class ToolErrorCode(str, Enum):
    """Standard error codes for tool invocations."""
    NOT_FOUND = "tool_not_found"
    INVALID_INPUT = "invalid_input"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    INTERNAL_ERROR = "internal_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    VALIDATION_ERROR = "validation_error"


class ToolError(Exception):
    """Error during tool invocation."""
    
    def __init__(
        self,
        message: str,
        code: ToolErrorCode = ToolErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_result(self) -> ToolResult:
        """Convert to ToolResult."""
        return ToolResult(
            success=False,
            error=self.message,
            error_code=self.code.value,
            metadata=self.details,
        )


@dataclass
class ToolInvocation:
    """Record of a tool invocation for audit."""
    invocation_id: str
    tool_name: str
    input: ToolInput
    result: Optional[ToolResult] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "invocation_id": self.invocation_id,
            "tool_name": self.tool_name,
            "input": self.input.to_dict(),
            "result": self.result.to_dict() if self.result else None,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
