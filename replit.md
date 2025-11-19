# Agentic Application Framework (AAF)

## Overview

The Agentic Application Framework (AAF) is a decorator-based framework for building production-ready agentic applications. AAF distinguishes between **simple LLM calls** and **autonomous agents**, providing node-based workflow orchestration with conditional routing, MCP tool integration, and A2A protocol support. The framework emphasizes simplicity through decorators like `@node`, `@workflow_graph`, `@llm`, `@autonomous_agent`, `@mcp_tool`, and `@a2a`, enabling developers to build complex multi-agent workflows without boilerplate code.

## Recent Changes (Nov 2024)

**Major Architecture Shift: Decorator-Based Node Orchestration**
- Replaced protocol-based architecture with decorator-first approach
- Created `@node` decorator for workflow steps
- Created `@workflow_graph` with conditional routing (if-then-else logic)
- Renamed `@llm_agent` → `@llm` to clarify: simple LLM call ≠ autonomous agent
- Created `@autonomous_agent` for real agents with tools, memory, planning
- Created `@mcp_tool` and `@a2a` decorators for external integrations
- Archived old protocol-based files (main.py → main_old_protocol.py.bak, framework.py → framework_old_protocol.py.bak)

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Design Patterns

**Decorator-First Architecture**: AAF uses decorators to compose functionality without boilerplate code. Decorators can be stacked (e.g., `@node @llm`, `@node @mcp_tool`) for powerful combinations.

**Node-Based Workflow Orchestration**: Workflows are built as directed graphs of nodes, with conditional routing based on state. Similar to LangGraph but simpler and more Pythonic.

**State Container Pattern**: Workflow state is a simple dictionary passed between nodes. Each node receives state, processes it, and returns updated state.

**Clear Separation**: AAF distinguishes between:
- **Simple LLM calls** (`@llm`) - one-shot LLM invocation
- **Autonomous agents** (`@autonomous_agent`) - agents with tools, memory, planning, and autonomy

### Authentication & Security Architecture

Security is managed via **Token Injection via Middleware**, where middleware injects authentication tokens from the state's `token_map` into service calls based on a `requires_token` property. A **Two-Tier Security Model** offers a "Secure Mode" (automated token management) and an "Insecure Mode" (manual or unauthenticated calls), separating authentication concerns from business logic.

### Core Decorators

*   **`@node`**: Mark a function as a workflow node (step in workflow graph)
*   **`@workflow_graph`**: Orchestrate nodes with conditional routing and state management
*   **`@llm`**: Simple LLM call (one-shot, no autonomy)
*   **`@autonomous_agent`**: Real agent with tools, memory, planning, autonomy
*   **`@mcp_tool`**: Integrate MCP (Model Context Protocol) tools
*   **`@a2a`**: Agent-to-agent delegation via A2A protocol
*   **`@custom_tool`**: Create custom tools for agents
*   **`@validate`**, **`@guardrail`**, **`@requires_approval`**: Safety and validation
*   **`@with_memory`**, **`@retry`**, **`@plan_task`**: Additional agent capabilities
*   **`@stack`**: Compose multiple decorators into reusable stacks

### Workflow Example: Chat Client

```python
from aaf import node, workflow_graph, llm, mcp_tool, autonomous_agent

# Step 1: Determine intent
@node
@llm(model="openai:gpt-4")
def parse_intent(state):
    return {"intent": "database"}  # or "tool" or "research"

# Step 2a: Generate SQL
@node
@llm(model="openai:gpt-4")
def generate_sql(state):
    return {"sql": "SELECT * FROM users"}

# Step 2b: Call MCP tool
@node
@mcp_tool("search")
def search_web(state):
    return {"results": [...]}

# Step 2c: Autonomous agent
@node
@autonomous_agent(model="openai:gpt-4", tools=["search", "calculator"], memory=True)
def research(state):
    return {"findings": "..."}

# Orchestrate with conditional routing
@workflow_graph(
    start="parse_intent",
    routing={
        "parse_intent": lambda s: {"database": "generate_sql", "tool": "search_web", "research": "research"}[s["intent"]],
        "generate_sql": "END",
        "search_web": "END",
        "research": "END"
    },
    end="END"
)
def chat_workflow(user_query: str):
    return {"user_query": user_query}

# Use it
result = chat_workflow("Show me users")
```

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

## State Management

AAF provides **pluggable state backends** for workflow persistence:

### Built-in Backends
- **InMemoryStateManager**: Fast, transient (dev/testing)
- **FileStateManager**: File-based persistence
- **RedisStateBackend**: Fast caching, distributed, TTL support
- **PostgresStateBackend**: Persistent, reliable, queryable (works with Replit database)

### Usage
```python
from aaf.state_backends import PostgresStateBackend, WorkflowStateManager
import psycopg2
import os

# Use Replit's database
conn = psycopg2.connect(os.environ['DATABASE_URL'])
backend = PostgresStateBackend(conn)
state_mgr = WorkflowStateManager(backend)

# Save workflow state
state_mgr.save_workflow_state("workflow_123", {"step": 1}, ttl=3600)

# Load state
state = state_mgr.load_workflow_state("workflow_123")
```

### Custom Backends
Implement `StateBackend` interface for any database (MongoDB, DynamoDB, etc.)

## UI & Theming Integration

AAF provides **embeddable UI** with **customizable themes** via **CopilotKit integration**:

### CopilotKit (AG-UI Protocol) - Experimental
AAF includes experimental support for CopilotKit's AG-UI protocol.
Note: Real-time event streaming requires workflow callback hooks (planned for future release).

AAF workflows can be embedded in React apps using CopilotKit's beautiful UI components:

```tsx
import { CopilotKit } from '@copilotkit/react-core';
import { CopilotSidebar } from '@copilotkit/react-ui';

<CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
  <YourApp />
  <CopilotSidebar defaultOpen={true} />
</CopilotKit>
```

### Built-in Themes
- **Default**: Professional, general purpose
- **Dark**: Night mode, developer tools
- **Ocean**: Analytics dashboards
- **Forest**: Health, sustainability
- **Sunset**: Creative, energetic
- **Minimal**: Clean, distraction-free

### Custom Themes
```python
from aaf.ui_themes import AAFTheme, generate_theme_css

# Create custom theme
my_theme = AAFTheme(
    name="MyBrand",
    primary_color="#ff6b6b",
    secondary_color="#4ecdc4"
)

# Generate CSS
css = generate_theme_css(my_theme.name)
```

### Embeddable Widgets
Generate standalone HTML widgets that can be iframe'd into any application:

```python
from aaf.ui_themes import generate_html_embed

html = generate_html_embed(
    theme_name="dark",
    title="AI Assistant",
    height="600px"
)
# Save to file or serve via endpoint
```

## External Dependencies

*   **MCP (Model Context Protocol)**: External protocol for tool invocation, with `DummyMCPClient` for simulation.
*   **A2A (Agent-to-Agent Protocol)**: Protocol for inter-agent communication, with `DummyA2AClient` for demonstration.
*   **FastAPI**: Web framework for building the REST API.
*   **Uvicorn**: ASGI server for serving the FastAPI application.
*   **Pydantic**: Data validation and settings management library.
*   **LangGraph**: Used as a base for orchestration, with `LangGraphAdapter` integrating its capabilities.
*   **Logging**: Standard Python `logging` module for observability.
*   **Redis** (optional): For RedisStateBackend caching.
*   **psycopg2** (optional): For PostgresStateBackend persistence.