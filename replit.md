# Agentic Application Framework (AAF)

## Overview

The Agentic Application Framework (AAF) is a pluggable framework for building agentic applications with middleware support, service abstractions, and workflow orchestration. The framework provides a modular architecture that enables secure integration with external services (MCP tools, Agent-to-Agent communication) through a middleware-based request/response pipeline. The core design follows protocol-oriented programming principles, using abstract protocols to define contracts between components while allowing flexible implementations.

## User Preferences

Preferred communication style: Simple, everyday language.

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

### Service Integration Architecture

**MCP Tool Integration**: The `MCPToolService` wraps MCP (Model Context Protocol) tool clients, translating between the framework's state model and MCP's tool invocation model. Supports authenticated and unauthenticated tool calls.

**A2A Client Integration**: The `A2AClientService` enables agent-to-agent delegation, allowing one agent to invoke another agent's capabilities. Requires authentication tokens to establish trust between agents.

Both service types follow a common pattern:
1. Extract parameters from state
2. Retrieve authentication token if required
3. Execute protocol-specific client call
4. Package response back into state

## REST API Service

**FastAPI Integration**: The framework is exposed as a REST API service (`api.py`) that runs on port 5000. This allows agents to be created and executed via HTTP requests, making the framework accessible to any client that can make HTTP calls.

### API Endpoints

**GET /health**: Health check endpoint that returns service status
**POST /agent/execute**: Execute an agent with custom configuration, services, and security settings
**POST /demo/scenario1**: Run demo scenario 1 (secure MCP tool execution with authentication)
**POST /demo/scenario2**: Run demo scenario 2 (A2A delegation failure without authentication)

### Interactive Documentation

The FastAPI service provides built-in interactive documentation via:
- **Swagger UI**: Available at `http://localhost:5000/docs` - Interactive API explorer with request/response examples
- **ReDoc**: Available at `http://localhost:5000/redoc` - Alternative API documentation interface

### Request/Response Models

All API endpoints use Pydantic models for request validation and response serialization:
- `AgentExecutionRequest`: Defines agent configuration, services, security settings, and request payload
- `AgentExecutionResponse`: Returns execution results, metadata, or error information
- `ServiceConfig`: Configures individual services (MCP tools, A2A clients)

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

**No Database**: The framework is stateless and doesn't require persistent storage. All state is ephemeral and flows through the execution pipeline.

**No External APIs**: Current implementation uses dummy clients for demonstration. Production deployments would replace these with real MCP/A2A client implementations that communicate with external services.

**Extensibility Points**: The protocol-based design allows adding new:
- Service types (beyond MCP and A2A)
- Middleware components (rate limiting, caching, metrics)
- Orchestration strategies (parallel execution, conditional routing)
- Authentication mechanisms (OAuth, API keys, certificates)