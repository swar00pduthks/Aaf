# Agentic Application Framework (AAF)

## Overview

The Agentic Application Framework (AAF) is a decorator-based framework for building production-ready agentic applications. It facilitates the creation of complex multi-agent workflows through node-based orchestration, conditional routing, and seamless integration of various components. AAF aims to simplify the development of AI applications by clearly distinguishing between simple LLM calls and autonomous agents, providing robust tools for integration, validation, and collaboration. The framework includes a REST API for execution, pluggable state management, and an embeddable UI with theming.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Design Patterns

AAF employs a **Decorator-First Architecture** to compose functionality without boilerplate. **Node-Based Workflow Orchestration** allows workflows to be built as directed graphs with conditional routing. The **State Container Pattern** ensures state is managed as a simple dictionary passed between nodes. The framework clearly separates **simple LLM calls** (`@llm`) from **autonomous agents** (`@autonomous_agent`) that possess tools, memory, and planning capabilities.

### Authentication & Security

Security is handled via **Token Injection via Middleware**, which injects authentication tokens from a `token_map` in the workflow state. A **Two-Tier Security Model** offers "Secure Mode" for automated token management and "Insecure Mode" for manual or unauthenticated calls, separating security concerns from business logic.

### Core Decorators

AAF provides a rich set of decorators for defining workflow components and behaviors:
*   **`@node`**: Defines a workflow step.
*   **`@workflow_graph`**: Orchestrates nodes with conditional routing.
*   **`@llm`**: For simple, one-shot LLM calls.
*   **`@autonomous_agent`**: For sophisticated agents with tools, memory, and planning.
*   **`@mcp_tool`**: Integrates MCP (Model Context Protocol) tools.
*   **`@a2a`**: Enables Agent-to-Agent delegation via A2A protocol.
*   **`@custom_tool`**: For creating custom tools.
*   **Validation & Safety**: `@validate`, `@guardrail`, `@requires_approval`.
*   **Agent Capabilities**: `@with_memory`, `@retry`, `@plan_task`.
*   **Composition**: `@stack` for combining multiple decorators.

### Production-Ready Abstractions

The framework includes abstractions for **State Management** (e.g., `InMemoryStateManager`, `FileStateManager`), **Retry Logic**, **Agent Registry**, **Structured Logging**, **Memory Systems** (short-term and long-term), **Planning & Reasoning**, **Multi-Agent Collaboration** (Hierarchical, Sequential, Swarm, RoundRobin), and **Human-in-the-Loop** workflows (`ApprovalWorkflow`, `InterventionPoint`, `HumanFeedbackLoop`).

### REST API Service

A REST API is exposed via **FastAPI** on port 5000, allowing agent execution via HTTP. It includes endpoints for health checks, agent execution, state management, and an agent registry. Interactive documentation is available via Swagger UI and ReDoc.

### UI & Theming Integration

AAF supports an **embeddable UI** with **customizable themes** via **CopilotKit integration**. A `/api/copilotkit` endpoint allows embedding AAF workflows into React applications, providing features like SSE streaming, real-time progress, and compatibility with the AG-UI protocol. Built-in themes (Default, Dark, Ocean, Forest, Sunset, Minimal) and custom theme generation are supported, along with embeddable HTML widgets.

### Framework Adapters

AAF offers adapters (`LangGraphAdapter`, `MicrosoftAgentAdapter`, `CrewAIAdapter`, `AutoGenAdapter`) to integrate with popular agentic frameworks, conforming to AAF's `AbstractAgent` protocol.

### Enhanced Type-Safe Agents

The `EnhancedAgent` utilizes Pydantic for type-safe agents, offering generic result types, multi-provider LLM support, tool registration via decorators, streaming with validation, and dependency injection for robust agent execution.

### State Management

AAF provides **pluggable state backends** for workflow persistence, including `InMemoryStateManager`, `FileStateManager`, `RedisStateBackend`, and `PostgresStateBackend` (compatible with Replit database). Custom backends can be implemented.

### Event-Driven Human-in-the-Loop

AAF supports **event-driven approvals** using message brokers (Kafka, Redis Pub/Sub) for integration with enterprise workflow tools (e.g., Flowable, Apache Airflow, ServiceNow). This enables decoupled, asynchronous human intervention with audit trails.

### Databricks Integration

AAF integrates with **Databricks Gemini** as an LLM provider (supporting Gemini 2.5 Pro/Flash, Gemini 3 Pro) and **Databricks Genie** as a SQL agent for natural language to SQL queries against Unity Catalog.

## External Dependencies

*   **MCP (Model Context Protocol)**: External protocol for tool invocation.
*   **A2A (Agent-to-Agent Protocol)**: Protocol for inter-agent communication.
*   **FastAPI**: Web framework for the REST API.
*   **Uvicorn**: ASGI server.
*   **Pydantic**: Data validation.
*   **LangGraph**: Used for orchestration, integrated via an adapter.
*   **Logging**: Standard Python `logging` module.
*   **Redis** (optional): For `RedisStateBackend`.
*   **psycopg2** (optional): For `PostgresStateBackend`.