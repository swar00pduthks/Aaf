# Agentic Application Framework (AAF) - Quick Start Guide

Welcome to AAF! This guide will help you build your first agentic application in minutes.

## Installation

```bash
# The framework is ready to use - no installation needed
# Dependencies: fastapi, pydantic, uvicorn
```

## Running the API Server

The framework includes a REST API for easy integration:

```bash
python api.py
```

The server will start on `http://localhost:5000` with interactive Swagger UI at `/docs`.

## Your First Agent (5 minutes)

### Step 1: Import AAF Components

```python
from aaf import (
    AgenticFrameworkX,
    InMemoryShortTermMemory,
    SimpleTaskPlanner,
    ApprovalWorkflow
)
```

### Step 2: Create an Agent with Memory

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create memory for context retention
memory = InMemoryShortTermMemory(logger=logger, max_entries=50)

# Store some context
memory.add({
    "content": "User wants weather information",
    "metadata": {"type": "user_intent"}
})

# Search memories
results = memory.search("weather", limit=5)
print(f"Found {len(results)} relevant memories")
```

### Step 3: Plan a Task

```python
planner = SimpleTaskPlanner(logger=logger)

plan = planner.create_plan(
    goal="Get weather forecast for San Francisco",
    context={"location": "San Francisco", "days": 7},
    available_services=["mcp_tool_weather", "mcp_tool_search"]
)

print(f"Created plan with {len(plan)} steps")
for step in plan:
    print(f"  - {step['action']}: {step['description']}")
```

### Step 4: Use the REST API

```python
import requests

# Execute an agent via API
response = requests.post(
    "http://localhost:5000/agent/execute",
    json={
        "agent_id": "my_agent",
        "framework": "langgraph",
        "services": [
            {
                "service_type": "mcp_tool",
                "name": "search",
                "require_auth": False
            }
        ],
        "security": False,
        "context": {"user": "demo_user"},
        "token_map": {},
        "request": {
            "tool": "search",
            "query": "AI frameworks 2025"
        }
    }
)

result = response.json()
print(f"Agent response: {result}")
```

## Multi-Agent Collaboration

```python
from aaf import SequentialPattern
from aaf.framework import SimpleAgent

# Create specialized agents
researcher = SimpleAgent("researcher", logger)
writer = SimpleAgent("writer", logger)
reviewer = SimpleAgent("reviewer", logger)

# Set up sequential collaboration (pipeline)
pipeline = SequentialPattern(
    agents=[researcher, writer, reviewer],
    logger=logger
)

# Execute the pipeline
result = pipeline.execute(
    agents=[],
    initial_state={
        "request": {
            "topic": "Quantum computing breakthroughs",
            "task": "research and create a report"
        }
    }
)

print(f"Pipeline completed: {result['status']}")
```

## Human-in-the-Loop

```python
from aaf import ApprovalWorkflow, ApprovalStatus

workflow = ApprovalWorkflow(logger=logger)

# Request approval for sensitive operations
status = workflow.request_approval(
    action="Delete 1000 old records",
    context={"table": "users", "age_days": 365},
    timeout_seconds=300
)

if status == ApprovalStatus.APPROVED:
    print("Operation approved - proceeding...")
else:
    print(f"Operation {status.value} - aborting")
```

## Next Steps

1. **Explore Examples**: Check out `examples/complete_example.py` for comprehensive usage
2. **Read the User Guide**: See `USER_GUIDE.md` for detailed component documentation
3. **Try the API**: Visit `http://localhost:5000/docs` for interactive API documentation
4. **Build Your Agent**: Combine memory, planning, collaboration, and human-in-the-loop for powerful applications

## Common Patterns

### Pattern 1: Research Assistant

```python
memory = InMemoryShortTermMemory(logger=logger)
planner = SimpleTaskPlanner(logger=logger)

# Store user preferences
memory.add({"content": "User prefers detailed technical explanations"})

# Plan research task
plan = planner.create_plan(
    goal="Research and explain quantum entanglement",
    context={},
    available_services=["mcp_tool_search"]
)
```

### Pattern 2: Content Pipeline

```python
pipeline = SequentialPattern(
    agents=[research_agent, draft_agent, edit_agent, publish_agent],
    logger=logger
)

result = pipeline.execute(agents=[], initial_state={"request": {...}})
```

### Pattern 3: Autonomous Team

```python
from aaf import HierarchicalPattern

manager = SimpleAgent("manager", logger)
workers = [SimpleAgent(f"worker_{i}", logger) for i in range(3)]

team = HierarchicalPattern(
    manager_agent=manager,
    worker_agents=workers,
    logger=logger
)

result = team.execute(agents=[], initial_state={"request": {...}})
```

## API Endpoints

- `GET /health` - Health check
- `POST /agent/execute` - Execute custom agent
- `POST /demo/scenario1` - Demo: Authenticated MCP tool
- `POST /demo/scenario2` - Demo: A2A delegation failure
- `GET /state/agents` - List agents with stored state
- `GET /registry/agents` - List registered agents
- `GET /docs` - Interactive Swagger UI

## Need Help?

- Check `USER_GUIDE.md` for detailed documentation
- See `examples/` directory for more code samples
- Review `replit.md` for architecture details

Happy building with AAF! 🚀
