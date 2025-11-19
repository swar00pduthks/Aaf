# Agentic Application Framework (AAF)

## Overview

The Agentic Application Framework (AAF) is a pluggable framework for building agentic applications with middleware support, service abstractions, and workflow orchestration. The framework provides a modular architecture that enables secure integration with external services (MCP tools, Agent-to-Agent communication) through a middleware-based request/response pipeline. The core design follows protocol-oriented programming principles, using abstract protocols to define contracts between components while allowing flexible implementations.

## User Preferences

Preferred communication style: Simple, everyday language.

## AAF's Unique Value Proposition

**Decorator Philosophy**: Lambda-like simplicity for everything - agent creation, orchestration, validation, HITL, memory, retry, planning - all as simple decorators.

**Core Features**:
- `@agent` - Turn any function into an agent
- `@workflow` - Auto-orchestrate multiple agents
- `@validate`, `@guardrail` - Add safety rules
- `@requires_approval`, `@human_feedback` - Add human oversight
- `@with_memory` - Add context retention
- `@retry` - Add fault tolerance
- `@plan_task` - Add task planning
- `@stack` - Compose all features

**Target Users**: Teams using multiple frameworks (LangGraph + CrewAI + Microsoft) who want zero-boilerplate orchestration

## System Architecture

### Core Design Patterns

**Protocol-Oriented Architecture**: The framework uses Python Protocols (defined in `aaf/abstracts.py`) to establish interface contracts without tight coupling to concrete implementations. This allows multiple implementations of agents, orchestrators, middleware, and services to coexist and be swapped at runtime.

**Middleware Pipeline Pattern**: Service calls flow through a configurable middleware stack that can intercept, modify, and enhance requests/responses. Middleware components implement `before_execute()` and `after_execute()` hooks, enabling cross-cutting concerns like logging, authentication, and error handling to be applied uniformly.

**State Container Pattern**: All execution context flows through an `AbstractState` TypedDict that carries:
- Agent identity and context
- Token mappings for authentication
- Request/response payloads
- Execution metadata

This centralizes state management and makes the data flow explicit and traceable.

**Adapter Pattern for Orchestration**: The `LangGraphAdapter` provides a simplified workflow orchestrator that executes services sequentially while applying middleware. This abstracts away orchestration complexity and allows the framework to support different orchestration backends (LangGraph, custom state machines, etc.) through a common interface.

### Authentication & Security Architecture

**Token Injection via Middleware**: The framework implements security through middleware that injects authentication tokens from the state's `token_map` into service calls. Services declare whether they require tokens via the `requires_token` property.

**Two-Tier Security Model**:
1. **Secure Mode** (security=True): Framework automatically manages token injection through middleware, ensuring authenticated service calls
2. **Insecure Mode** (security=False): Services execute without automatic token management, allowing unauthenticated calls or manual token handling

This design separates authentication concerns from business logic, making security enforcement declarative rather than imperative.

### Component Responsibilities

**AgenticFrameworkX (Facade)**: Factory class that constructs agents with configured middleware stacks and orchestrators. Abstracts framework initialization complexity from users.

**AbstractAgent**: Represents an autonomous agent that can execute tasks using services. Maintains agent identity, state, and coordinates service execution through the orchestrator.

**AbstractService**: Protocol for external integrations (MCP tools, A2A agents). Each service implementation handles its own protocol-specific communication while conforming to the common interface.

**AbstractMiddleware**: Interceptor components that process state before/after service execution. Enables composition of cross-cutting concerns.

**AbstractWorkflowOrchestrator**: Coordinates service execution flow, applying middleware and managing state transitions.

**AbstractStateManager**: Protocol for persisting and retrieving agent state. Enables agents to maintain state across executions and recover from failures.

**AbstractRetryPolicy**: Protocol for defining retry behavior when service calls fail. Supports configurable retry strategies with exponential backoff.

**AbstractAgentRegistry**: Protocol for centralized agent lifecycle management, including registration, lookup, and shutdown coordination.

### Service Integration Architecture

**MCP Tool Integration**: The `MCPToolService` wraps MCP (Model Context Protocol) tool clients, translating between the framework's state model and MCP's tool invocation model. Supports authenticated and unauthenticated tool calls.

**A2A Client Integration**: The `A2AClientService` enables agent-to-agent delegation, allowing one agent to invoke another agent's capabilities. Requires authentication tokens to establish trust between agents.

Both service types follow a common pattern:
1. Extract parameters from state
2. Retrieve authentication token if required
3. Execute protocol-specific client call
4. Package response back into state

### Production-Ready Abstractions

**State Management**: The framework includes `InMemoryStateManager` for ephemeral state and `FileStateManager` for persistent JSON-based state storage. State managers handle:
- Agent state persistence across executions
- Atomic save/load operations
- State lifecycle management (list, delete, clear)
- Metadata tracking (timestamps, versions)

**Retry Logic**: The `RetryPolicy` abstraction enables configurable retry behavior for transient failures:
- Exponential backoff with jitter
- Configurable max retries and delays
- Exception-specific retry rules
- `RetryMiddleware` integrates retry logic into the middleware pipeline
- `@with_retry` decorator for function-level retry support

**Agent Registry**: The `AgentRegistry` provides centralized agent lifecycle management:
- Agent registration with metadata
- Duplicate prevention with optional replacement
- Agent lookup and information retrieval
- Coordinated shutdown of all registered agents
- Execution statistics tracking

**Structured Logging**: The `StructuredLogger` enhances observability with:
- Context-aware logging with correlation IDs
- Structured data attachment to log entries
- Automatic context enrichment (timestamp, level, module)
- Integration with standard Python logging

**Memory Systems**: The framework provides memory abstractions for context retention:
- `InMemoryShortTermMemory`: Fast working memory with TTL and size limits
- `SimpleLongTermMemory`: Persistent semantic memory for knowledge retention
- Support for metadata filtering and relevance scoring
- Designed for future integration with vector databases (Pinecone, Qdrant, etc.)

**Planning & Reasoning**: Task decomposition and ReAct pattern support:
- `SimpleTaskPlanner`: Break down complex goals into executable steps
- `ReActReasoner`: Reason + Act pattern for step-by-step problem solving
- Plan refinement based on feedback and execution results
- Extensible for LLM-driven dynamic planning

**Multi-Agent Collaboration**: Four collaboration patterns for coordinating agents:
- `HierarchicalPattern`: Manager-worker delegation (inspired by LangGraph supervisor)
- `SequentialPattern`: Pipeline execution (inspired by CrewAI task sequences)
- `SwarmPattern`: Parallel autonomous execution (inspired by OpenAI Swarm)
- `RoundRobinPattern`: Iterative refinement through agent rotation

**Human-in-the-Loop**: Production-ready oversight capabilities:
- `ApprovalWorkflow`: Request human approval for sensitive operations
- `InterventionPoint`: Define when human input is required
- `HumanFeedbackLoop`: Continuous human guidance and corrections
- `GuardrailValidator`: Safety rules and policy enforcement

## REST API Service

**FastAPI Integration**: The framework is exposed as a REST API service (`api.py`) that runs on port 5000. This allows agents to be created and executed via HTTP requests, making the framework accessible to any client that can make HTTP calls.

### API Endpoints

#### Core Execution
**GET /health**: Health check endpoint that returns service status
**POST /agent/execute**: Execute an agent with custom configuration, services, and security settings
**POST /demo/scenario1**: Run demo scenario 1 (secure MCP tool execution with authentication)
**POST /demo/scenario2**: Run demo scenario 2 (A2A delegation failure without authentication)

#### State Management
**GET /state/agents**: List all agents with stored state
**POST /state/{agent_id}**: Save agent state
**GET /state/{agent_id}**: Load agent state
**DELETE /state/{agent_id}**: Delete agent state

#### Agent Registry
**GET /registry/agents**: List all registered agents
**GET /registry/{agent_id}**: Get information about a registered agent
**GET /registry**: Get information about all registered agents
**DELETE /registry/{agent_id}**: Unregister an agent from the registry

### Interactive Documentation

The FastAPI service provides built-in interactive documentation via:
- **Swagger UI**: Available at `http://localhost:5000/docs` - Interactive API explorer with request/response examples
- **ReDoc**: Available at `http://localhost:5000/redoc` - Alternative API documentation interface

### Request/Response Models

All API endpoints use Pydantic models for request validation and response serialization:
- `AgentExecutionRequest`: Defines agent configuration, services, security settings, and request payload
- `AgentExecutionResponse`: Returns execution results, metadata, or error information
- `ServiceConfig`: Configures individual services (MCP tools, A2A clients)

## Framework Adapters

AAF provides built-in adapters for seamless integration with popular agentic frameworks. These adapters eliminate the need for users to write custom wrapper classes.

### Built-in Adapters (aaf/adapters.py)

**LangGraphAdapter**: Wraps LangGraph agents to work with AAF protocols
- Enables orchestration of LangGraph's stateful workflows
- Adds AAF's REST API, memory, and HITL features
- Usage: `LangGraphAdapter("agent_id", langgraph_agent)`

**MicrosoftAgentAdapter**: Wraps Microsoft Agent Framework agents
- Integrates with Microsoft's multi-agent patterns
- Adds AAF production infrastructure
- Usage: `MicrosoftAgentAdapter("agent_id", microsoft_agent)`

**CrewAIAdapter**: Wraps CrewAI role-based agents
- Combines CrewAI's collaboration with AAF's guardrails
- Provides memory and planning on top of CrewAI
- Usage: `CrewAIAdapter("agent_id", crewai_agent)`

**AutoGenAdapter**: Wraps AutoGen conversation agents
- Orchestrates AutoGen multi-agent conversations
- Adds state management and REST API
- Usage: `AutoGenAdapter("agent_id", autogen_agent)`

**Design Pattern**: Adapter pattern ensures all framework-specific agents conform to AAF's `AbstractAgent` protocol without requiring users to understand protocols or write boilerplate wrapper code.

## Enhanced Type-Safe Agents (NEW!)

**aaf/enhanced_agent.py**: Pydantic AI-like type-safe agents with full validation

**Features**:
- Generic result types with Pydantic validation
- Multi-provider LLM support (OpenAI, Anthropic, Gemini, +more)
- Tool registration with `@agent.tool` decorator
- Streaming with validation
- Dependency injection
- FastAPI-like ergonomics

**Example**:
```python
from pydantic import BaseModel
from aaf import EnhancedAgent

class ResearchOutput(BaseModel):
    summary: str
    findings: list[str]

agent = EnhancedAgent(
    agent_id="researcher",
    model="openai:gpt-4",
    result_type=ResearchOutput  # Type-safe!
)

result = agent.run_sync("Research quantum computing")
```

**Target Users**: Developers who want Pydantic AI-like type safety with AAF's orchestration

## Simplified API

**aaf/simplified_api.py**: High-level API facade that completely hides protocol complexity
- `create_agent()`: Simple agent creation
- `create_memory()`: Memory management without protocols
- `create_team()`: Multi-agent teams in one line
- `create_planner()`: Task planning without abstractions

**Target Users**: Developers who want quick prototyping without learning AAF's architecture

## External Dependencies

### Protocol Implementations

**MCP (Model Context Protocol)**: External protocol for tool invocation. The framework provides `DummyMCPClient` as a reference implementation that simulates MCP tool calls with optional authentication.

**A2A (Agent-to-Agent Protocol)**: Protocol for inter-agent communication. The framework includes `DummyA2AClient` to demonstrate agent delegation patterns with authentication requirements.

### Framework Dependencies

**FastAPI**: Production-ready web framework for building REST APIs with automatic OpenAPI/Swagger documentation, request validation via Pydantic, and async support.

**Uvicorn**: ASGI server for serving the FastAPI application with auto-reload during development.

**Pydantic**: Data validation library used for API request/response models and type safety.

**LangGraph**: The framework is designed to integrate with LangGraph for advanced state graph orchestration. The current `LangGraphAdapter` provides a simplified linear execution model, but the architecture supports full LangGraph capabilities (conditional edges, parallel execution, state persistence).

**Logging**: Uses Python's standard `logging` module for debugging and monitoring. The `LoggingMiddleware` demonstrates how cross-cutting concerns integrate into the execution pipeline.

### Design Considerations

**Optional State Persistence**: The framework supports both stateless (in-memory) and stateful (file-based) execution modes. Agents can persist state across executions using the state manager abstraction.

**No External APIs**: Current implementation uses dummy clients for demonstration. Production deployments would replace these with real MCP/A2A client implementations that communicate with external services.

**Extensibility Points**: The protocol-based design allows adding new:
- Service types (beyond MCP and A2A)
- Middleware components (rate limiting, caching, metrics)
- Orchestration strategies (parallel execution, conditional routing)
- Authentication mechanisms (OAuth, API keys, certificates)