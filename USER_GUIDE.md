# AAF User Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Memory Systems](#memory-systems)
4. [Planning & Reasoning](#planning--reasoning)
5. [Multi-Agent Collaboration](#multi-agent-collaboration)
6. [Human-in-the-Loop](#human-in-the-loop)
7. [State Management](#state-management)
8. [Retry Logic](#retry-logic)
9. [API Reference](#api-reference)

## Architecture Overview

AAF follows a protocol-oriented architecture with these key design patterns:

- **Protocol-based**: All components implement abstract protocols for flexibility
- **Middleware pipeline**: Request/response flows through configurable middleware
- **State container**: Explicit state management through AbstractState
- **Service abstraction**: Unified interface for MCP tools, A2A agents, etc.

## Core Components

### 1. Agents (`AbstractAgent`)

Agents are autonomous entities that execute tasks using available services.

```python
from aaf.framework import SimpleAgent
import logging

logger = logging.getLogger(__name__)
agent = SimpleAgent("my_agent", logger)

result = agent.execute({"task": "analyze data"})
```

### 2. Services (`AbstractService`)

Services represent external integrations (MCP tools, APIs, other agents).

```python
# Services are created via the API:
service_config = {
    "service_type": "mcp_tool",
    "name": "search",
    "require_auth": True
}
```

### 3. Middleware (`AbstractMiddleware`)

Middleware intercepts and transforms requests/responses.

Available middleware:
- `AuthMiddleware` - Token injection for authentication
- `LoggingMiddleware` - Request/response logging
- `RetryMiddleware` - Automatic retry with exponential backoff

## Memory Systems

AAF provides two memory implementations:

### Short-Term Memory

For conversation context and working memory:

```python
from aaf import InMemoryShortTermMemory

memory = InMemoryShortTermMemory(
    logger=logger,
    max_entries=100,      # Max memories to retain
    ttl_seconds=3600      # Expire after 1 hour
)

# Add a memory
memory.add({
    "content": "User prefers technical details",
    "metadata": {"type": "preference", "confidence": 0.9}
})

# Search memories
results = memory.search("technical", limit=10)

# Get recent memories
recent = memory.get_recent(count=5)
```

### Long-Term Memory

For persistent knowledge across sessions:

```python
from aaf import SimpleLongTermMemory

lt_memory = SimpleLongTermMemory(logger=logger)

# Store long-term knowledge
lt_memory.add({
    "content": "Company policy: All deletions require approval",
    "metadata": {"type": "policy", "department": "IT"}
})

# Search with metadata filter
policies = lt_memory.search(
    "approval",
    metadata_filter={"type": "policy"}
)
```

## Planning & Reasoning

### Task Planning

Break down complex goals into executable steps:

```python
from aaf import SimpleTaskPlanner

planner = SimpleTaskPlanner(logger=logger)

plan = planner.create_plan(
    goal="Research AI safety and create a summary",
    context={"audience": "technical", "length": "short"},
    available_services=["mcp_tool_search", "a2a_client_writer"]
)

# Plan refinement based on feedback
refined_plan = planner.refine_plan(
    plan=plan,
    feedback={"status": "error", "error": "Permission denied"}
)
```

### ReAct Reasoning

Implement Reason + Act pattern for step-by-step problem solving:

```python
from aaf import ReActReasoner

reasoner = ReActReasoner(logger=logger)

reasoning = reasoner.reason(
    observation="Task started successfully",
    history=[],
    goal="Complete the research task"
)

print(f"Thought: {reasoning['thought']}")
print(f"Action: {reasoning['action']['type']}")

# Get reasoning history
summary = reasoner.summarize_reasoning()
```

## Multi-Agent Collaboration

AAF supports four collaboration patterns:

### 1. Hierarchical Pattern (Manager-Worker)

```python
from aaf import HierarchicalPattern
from aaf.framework import SimpleAgent

manager = SimpleAgent("manager", logger)
workers = [
    SimpleAgent("researcher", logger),
    SimpleAgent("analyst", logger),
    SimpleAgent("writer", logger)
]

hierarchy = HierarchicalPattern(
    manager_agent=manager,
    worker_agents=workers,
    logger=logger
)

result = hierarchy.execute(
    agents=[],
    initial_state={"request": {"task": "Analyze Q4 earnings"}}
)
```

### 2. Sequential Pattern (Pipeline)

```python
from aaf import SequentialPattern

pipeline = SequentialPattern(
    agents=[research_agent, draft_agent, edit_agent],
    logger=logger
)

result = pipeline.execute(
    agents=[],
    initial_state={"request": {"topic": "AI trends"}}
)
```

### 3. Swarm Pattern (Parallel Autonomous)

```python
from aaf import SwarmPattern

swarm = SwarmPattern(
    agents=[agent1, agent2, agent3],
    logger=logger
)

result = swarm.execute(
    agents=[],
    initial_state={"request": {"task": "distributed analysis"}}
)
```

### 4. Round-Robin Pattern (Iterative Refinement)

```python
from aaf import RoundRobinPattern

round_robin = RoundRobinPattern(
    agents=[agent1, agent2, agent3],
    max_iterations=3,
    logger=logger
)

result = round_robin.execute(
    agents=[],
    initial_state={"request": {"draft": "Initial content"}}
)
```

## Human-in-the-Loop

### Approval Workflows

Require human approval for sensitive operations:

```python
from aaf import ApprovalWorkflow, ApprovalStatus

def custom_approver(request):
    print(f"Approval needed: {request['action']}")
    # In production: integrate with UI, email, Slack, etc.
    return ApprovalStatus.APPROVED

workflow = ApprovalWorkflow(
    approval_handler=custom_approver,
    logger=logger
)

status = workflow.request_approval(
    action="Delete user data",
    context={"user_id": "12345", "reason": "GDPR request"},
    timeout_seconds=300
)

if status == ApprovalStatus.APPROVED:
    # Proceed with operation
    pass
```

### Intervention Points

Define when human input is needed:

```python
from aaf import InterventionPoint

def needs_review(context):
    return context.get("confidence", 1.0) < 0.7

intervention = InterventionPoint(
    name="low_confidence_check",
    condition=needs_review,
    timeout_seconds=60,
    logger=logger
)

if intervention.should_intervene({"confidence": 0.5}):
    # Request human review
    pass
```

### Guardrails

Validate actions against safety rules:

```python
from aaf import GuardrailValidator

rules = [
    {
        "name": "no_bulk_delete",
        "condition": lambda action: action.get("type") == "delete" and action.get("count", 0) > 100,
        "message": "Cannot delete more than 100 items at once",
        "severity": "high"
    }
]

validator = GuardrailValidator(rules=rules, logger=logger)

action = {"type": "delete", "count": 500}
is_safe = validator.validate(action)

if not is_safe:
    violations = validator.get_violations()
    print(f"Blocked: {violations}")
```

## State Management

Persist agent state across executions:

```python
from aaf import InMemoryStateManager

state_mgr = InMemoryStateManager(logger=logger)

# Save state
state_mgr.save_state(
    agent_id="my_agent",
    state={"step": 3, "data": {...}}
)

# Load state
state = state_mgr.load_state("my_agent")

# List all agents with state
agents = state_mgr.list_agents()

# Delete state
state_mgr.delete_state("my_agent")
```

## Retry Logic

Handle transient failures automatically:

```python
from aaf import RetryPolicy, with_retry

# Create retry policy
policy = RetryPolicy(
    max_retries=3,
    initial_delay=1.0,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True
)

# Use as decorator
@with_retry(retry_policy=policy)
def unstable_operation():
    # May fail transiently
    pass

# Retry middleware is automatically applied in the framework
```

## API Reference

### REST Endpoints

#### Core Execution
- `POST /agent/execute` - Execute an agent with custom configuration
- `GET /health` - Health check

#### Demo Scenarios
- `POST /demo/scenario1` - Authenticated MCP tool usage
- `POST /demo/scenario2` - A2A delegation without auth (fails)

#### State Management
- `GET /state/agents` - List all agents with stored state
- `POST /state/{agent_id}` - Save agent state
- `GET /state/{agent_id}` - Load agent state
- `DELETE /state/{agent_id}` - Delete agent state

#### Agent Registry
- `GET /registry/agents` - List registered agents
- `GET /registry/{agent_id}` - Get agent info
- `DELETE /registry/{agent_id}` - Unregister agent

### Request Format

```json
{
  "agent_id": "my_agent",
  "framework": "langgraph",
  "services": [
    {
      "service_type": "mcp_tool",
      "name": "search",
      "require_auth": false
    }
  ],
  "security": true,
  "context": {"user": "demo"},
  "token_map": {},
  "request": {"query": "test"}
}
```

### Response Format

```json
{
  "agent_id": "my_agent",
  "status": "success",
  "response": {...},
  "metadata": {...},
  "error": null
}
```

## Best Practices

1. **Use Memory for Context**: Store user preferences and conversation history
2. **Plan Before Acting**: Use planners to decompose complex tasks
3. **Choose the Right Pattern**: Match collaboration pattern to your use case
4. **Add Human Oversight**: Use approval workflows for sensitive operations
5. **Implement Guardrails**: Validate all actions against safety rules
6. **Enable Retry Logic**: Handle transient failures automatically
7. **Persist State**: Save agent state for long-running tasks

## Next Steps

- Explore `examples/complete_example.py` for comprehensive code samples
- Try the interactive Swagger UI at `/docs`
- Build your first multi-agent system
- Integrate with external LLM APIs for dynamic planning

For more information, see `replit.md` for architecture details.
