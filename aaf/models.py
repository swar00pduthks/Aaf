"""
Pydantic models for type-safe agent interactions.

This module replaces TypedDict with full Pydantic validation,
bringing type safety on par with Pydantic AI.
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class AgentMetadata(BaseModel):
    """Metadata about agent execution."""
    agent_id: str
    framework: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time: Optional[float] = None
    
    model_config = ConfigDict(extra='allow')


class AgentRequest(BaseModel):
    """Type-safe agent request with validation."""
    task: Optional[str] = None
    query: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra='allow')


class AgentResponse(BaseModel):
    """Type-safe agent response with validation."""
    status: Literal["success", "error", "pending"] = "success"
    result: Any
    metadata: AgentMetadata
    error: Optional[str] = None
    
    model_config = ConfigDict(extra='allow')


class MemoryEntry(BaseModel):
    """Type-safe memory entry."""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    relevance_score: Optional[float] = None


class PlanStep(BaseModel):
    """Type-safe planning step."""
    action: str = Field(description="The action to perform")
    description: str = Field(description="Detailed description of the step")
    dependencies: List[str] = Field(default_factory=list)
    expected_output: Optional[str] = None


class GuardrailViolation(BaseModel):
    """Type-safe guardrail violation."""
    rule: str
    message: str
    severity: Literal["low", "medium", "high", "critical"]
    action: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class StateSnapshot(BaseModel):
    """Type-safe state snapshot."""
    agent_id: str
    state: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    version: int = 1
    
    model_config = ConfigDict(extra='allow')
