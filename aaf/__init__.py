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
# Old framework import removed (now using decorator-based approach)
from aaf.state import InMemoryStateManager, FileStateManager

# Pluggable state backends (Redis, PostgreSQL, etc.)
from aaf.state_backends import (
    StateBackend,
    RedisStateBackend,
    PostgresStateBackend,
    WorkflowStateManager,
)

# UI/Theming - CopilotKit integration and embeddable widgets
from aaf.agui_adapter import (
    AAFAGUIAdapter,
    create_agui_fastapi_endpoint,
)
from aaf.ui_themes import (
    AAFTheme,
    THEMES,
    get_theme,
    generate_theme_css,
    generate_html_embed,
)

# Databricks integration (Gemini LLM & Genie SQL agent)
from aaf.databricks_integration import (
    DatabricksGeminiProvider,
    DatabricksGenieAgent,
    create_databricks_gemini_llm,
    create_databricks_genie_agent,
)

# Event-driven Human-in-the-Loop (Kafka, Redis, etc.)
from aaf.event_driven_hitl import (
    MessageBroker,
    KafkaMessageBroker,
    RedisMessageBroker,
    EventDrivenHumanApproval,
    requires_event_approval,
)
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

# LLM decorators (AAF's own - no Pydantic AI dependency)
from aaf.llm_decorators import (
    llm,  # Simple LLM call (not an agent)
    multi_provider_agent,  # Multi-provider with fallback
)

# Workflow nodes and orchestration
from aaf.workflow_nodes import (
    node,
    workflow_graph,
    WorkflowNode,
    WorkflowGraph,
    get_node,
    list_nodes,
)

# Tool decorators (MCP, A2A, custom)
from aaf.tool_decorators import (
    mcp_tool,
    a2a_agent as a2a,  # Rename for clarity
    custom_tool,
)

# Autonomous agent (real agent with tools, memory, planning)
from aaf.autonomous_agent_decorator import (
    autonomous_agent,
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
    # "AgenticFrameworkX",  # Removed - old protocol-based approach
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
    "llm",
    "multi_provider_agent",
    "node",
    "workflow_graph",
    "mcp_tool",
    "a2a",
    "custom_tool",
    "autonomous_agent",
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
