"""
Agentic Application Framework (AAF)

A pluggable framework for building agentic applications with middleware support,
service abstractions, and workflow orchestration.
"""

from aaf.abstracts import (
    AbstractAgent,
    AbstractWorkflowOrchestrator,
    AbstractMiddleware,
    AbstractService,
    AbstractState,
    AbstractMemory,
    AbstractPlanner,
    AbstractReasoner,
    MemoryEntry,
)
from aaf.framework import AgenticFrameworkX
from aaf.state import InMemoryStateManager, FileStateManager
from aaf.retry import RetryPolicy, RetryMiddleware, with_retry
from aaf.registry import AgentRegistry, AgentInfo
from aaf.structured_logging import StructuredLogger, LoggingContext
from aaf.memory import InMemoryShortTermMemory, SimpleLongTermMemory
from aaf.planning import SimpleTaskPlanner, ReActReasoner
from aaf.collaboration import (
    HierarchicalPattern,
    SequentialPattern,
    SwarmPattern,
    RoundRobinPattern,
)
from aaf.human_loop import (
    ApprovalWorkflow,
    ApprovalStatus,
    InterventionPoint,
    HumanFeedbackLoop,
    GuardrailValidator,
)

# Framework adapters for easy integration
from aaf.adapters import (
    LangGraphAdapter,
    MicrosoftAgentAdapter,
    CrewAIAdapter,
    AutoGenAdapter,
)

# Zero-boilerplate decorators (AAF's STANDOUT feature!)
from aaf.decorators import (
    agent,
    langgraph_agent,
    crewai_agent,
    microsoft_agent,
    workflow,
    get_agent,
    list_agents,
)

# Pydantic AI-powered decorators (optional - requires pydantic-ai)
try:
    from aaf.pydantic_decorators import (
        pydantic_agent,
        chatbot,
        from_pydantic_ai,
    )
    PYDANTIC_AI_INTEGRATION = True
except ImportError:
    PYDANTIC_AI_INTEGRATION = False
    pydantic_agent = None
    chatbot = None
    from_pydantic_ai = None

# Feature decorators (validators, HITL, memory, retry, etc.)
from aaf.feature_decorators import (
    validate,
    guardrail,
    no_bulk_operations,
    requires_approval,
    human_feedback,
    with_memory,
    retry,
    plan_task,
    log_execution,
    stack,
)

# Enhanced type-safe agents (optional - for Pydantic AI-like features)
from aaf.enhanced_agent import EnhancedAgent
from aaf.models import (
    AgentRequest,
    AgentResponse,
    AgentMetadata,
    MemoryEntry,
    PlanStep,
)
from aaf.llm_providers import (
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    infer_provider,
)

# Simplified API (optional - hides protocol complexity)
try:
    from aaf import simplified_api
except ImportError:
    simplified_api = None

__all__ = [
    "AbstractAgent",
    "AbstractWorkflowOrchestrator",
    "AbstractMiddleware",
    "AbstractService",
    "AbstractState",
    "AbstractMemory",
    "AbstractPlanner",
    "AbstractReasoner",
    "MemoryEntry",
    "AgenticFrameworkX",
    "InMemoryStateManager",
    "FileStateManager",
    "RetryPolicy",
    "RetryMiddleware",
    "with_retry",
    "AgentRegistry",
    "AgentInfo",
    "StructuredLogger",
    "LoggingContext",
    "InMemoryShortTermMemory",
    "SimpleLongTermMemory",
    "SimpleTaskPlanner",
    "ReActReasoner",
    "HierarchicalPattern",
    "SequentialPattern",
    "SwarmPattern",
    "RoundRobinPattern",
    "ApprovalWorkflow",
    "ApprovalStatus",
    "InterventionPoint",
    "HumanFeedbackLoop",
    "GuardrailValidator",
    "LangGraphAdapter",
    "MicrosoftAgentAdapter",
    "CrewAIAdapter",
    "AutoGenAdapter",
    "agent",
    "langgraph_agent",
    "crewai_agent",
    "microsoft_agent",
    "workflow",
    "get_agent",
    "list_agents",
    "validate",
    "guardrail",
    "no_bulk_operations",
    "requires_approval",
    "human_feedback",
    "with_memory",
    "retry",
    "plan_task",
    "log_execution",
    "stack",
    "pydantic_agent",
    "chatbot",
    "from_pydantic_ai",
    "EnhancedAgent",
    "AgentRequest",
    "AgentResponse",
    "AgentMetadata",
    "MemoryEntry",
    "PlanStep",
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
    "infer_provider",
]
