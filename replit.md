# Agentic Application Framework (AAF)

## Overview

The Agentic Application Framework (AAF) is a pluggable framework for building agentic applications, emphasizing a modular architecture with middleware support, service abstractions, and workflow orchestration. It enables secure integration with external services (MCP tools, Agent-to-Agent communication) via a middleware-based request/response pipeline. The framework's core design uses protocol-oriented programming principles to define contracts between components, allowing for flexible implementations. AAF provides a decorator-based approach for common agentic features like agent creation, orchestration, validation, human-in-the-loop (HITL), memory, retry mechanisms, and planning, aiming to simplify complex multi-framework workflows.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Design Patterns

The framework is built on **Protocol-Oriented Architecture** (Python Protocols) for defining interface contracts, allowing flexible and swappable implementations. A **Middleware Pipeline Pattern** enables intercepting and modifying service requests/responses for cross-cutting concerns like logging and authentication. The **State Container Pattern** centralizes execution context through an `AbstractState` TypedDict, ensuring explicit and traceable data flow. An **Adapter Pattern** is used for orchestration, with `LangGraphAdapter` providing a simplified workflow executor, abstracting complexity and allowing integration with various orchestration backends.

### Authentication & Security Architecture

Security is managed via **Token Injection via Middleware**, where middleware injects authentication tokens from the state's `token_map` into service calls based on a `requires_token` property. A **Two-Tier Security Model** offers a "Secure Mode" (automated token management) and an "Insecure Mode" (manual or unauthenticated calls), separating authentication concerns from business logic.

### Component Responsibilities

*   **AgenticFrameworkX (Facade)**: Factory for constructing agents with configured middleware and orchestrators.
*   **AbstractAgent**: Represents an autonomous agent, managing identity, state, and service execution.
*   **AbstractService**: Protocol for external integrations (MCP tools, A2A agents).
*   **AbstractMiddleware**: Intercepts and processes state before/after service execution.
*   **AbstractWorkflowOrchestrator**: Coordinates service execution flow and state transitions.
*   **AbstractStateManager**: Protocol for persisting and retrieving agent state.
*   **AbstractRetryPolicy**: Protocol for defining retry behavior.
*   **AbstractAgentRegistry**: Protocol for centralized agent lifecycle management.

### Service Integration Architecture

**MCP Tool Integration** uses `MCPToolService` to wrap MCP tool clients, handling translation and authentication. **A2A Client Integration** uses `A2AClientService` for agent-to-agent delegation, requiring authentication. Both follow a pattern of parameter extraction, token retrieval, client execution, and response packaging.

### Production-Ready Abstractions

The framework includes abstractions for **State Management** (`InMemoryStateManager`, `FileStateManager`), **Retry Logic** (configurable policies with exponential backoff, `RetryMiddleware`), **Agent Registry** (centralized lifecycle management), **Structured Logging** (context-aware logging), **Memory Systems** (`InMemoryShortTermMemory`, `SimpleLongTermMemory` for context retention), **Planning & Reasoning** (`SimpleTaskPlanner`, `ReActReasoner`), **Multi-Agent Collaboration** (Hierarchical, Sequential, Swarm, RoundRobin patterns), and **Human-in-the-Loop** (`ApprovalWorkflow`, `InterventionPoint`, `HumanFeedbackLoop`, `GuardrailValidator`).

### REST API Service

The framework exposes a REST API via **FastAPI** on port 5000, allowing agents to be created and executed via HTTP.
**API Endpoints** include `/health`, `/agent/execute`, demo scenarios, and endpoints for state management (`/state/*`) and agent registry (`/registry/*`). Interactive documentation is available via **Swagger UI** (`/docs`) and **ReDoc** (`/redoc`). Pydantic models are used for request/response validation.

### Framework Adapters

AAF provides built-in adapters (`LangGraphAdapter`, `MicrosoftAgentAdapter`, `CrewAIAdapter`, `AutoGenAdapter`) to integrate with popular agentic frameworks, ensuring they conform to AAF's `AbstractAgent` protocol without custom wrapper code.

### Enhanced Type-Safe Agents

The `EnhancedAgent` (using Pydantic AI-like features) offers type-safe agents with generic result types, multi-provider LLM support, tool registration via decorators, streaming with validation, and dependency injection, focusing on robust and validated agent execution.

### Simplified API

A high-level `simplified_api.py` facade hides protocol complexity for rapid prototyping, offering functions like `create_agent()`, `create_memory()`, `create_team()`, and `create_planner()`.

## External Dependencies

*   **MCP (Model Context Protocol)**: External protocol for tool invocation, with `DummyMCPClient` for simulation.
*   **A2A (Agent-to-Agent Protocol)**: Protocol for inter-agent communication, with `DummyA2AClient` for demonstration.
*   **FastAPI**: Web framework for building the REST API.
*   **Uvicorn**: ASGI server for serving the FastAPI application.
*   **Pydantic**: Data validation and settings management library.
*   **LangGraph**: Used as a base for orchestration, with `LangGraphAdapter` integrating its capabilities.
*   **Logging**: Standard Python `logging` module for observability.