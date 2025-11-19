# AAF Integration Guide

## Overview

AAF can work **alongside** other agentic frameworks (LangGraph, Microsoft Agent Framework, CrewAI) rather than replacing them. Use AAF as:

1. **Orchestration Layer** - Coordinate agents from multiple frameworks
2. **Production Infrastructure** - Add REST API, memory, guardrails, and HITL to any framework
3. **Middleware Layer** - Provide retry logic, auth, state management on top of existing agents

## Integration Patterns

### Pattern 1: AAF as Orchestration Layer

Use AAF to orchestrate agents built with other frameworks:

```
AAF Orchestration (SequentialPattern/HierarchicalPattern)
    ↓
LangGraph Agent 1 → Microsoft Agent 2 → CrewAI Agent 3
```

**When to use**: You have agents from different frameworks and need unified orchestration

**Example**: See `examples/integration_langgraph.py`

### Pattern 2: AAF as Production Infrastructure

Wrap framework agents to add production features:

```
AAF REST API + Memory + Guardrails + HITL
    ↓
Your Agent (LangGraph/Microsoft/CrewAI)
```

**When to use**: You have existing agents but need:
- REST API exposure
- Memory management
- Human-in-the-loop workflows
- State persistence
- Approval workflows
- Safety guardrails

**Example**: See `examples/integration_microsoft_agent.py`

### Pattern 3: Hybrid Approach

Combine AAF components with framework-specific features:

```
AAF Memory + AAF Planning
    ↓
LangGraph Stateful Workflow
    ↓
AAF Approval Workflow + AAF Guardrails
```

**When to use**: You want best of both worlds

**Example**: See `examples/integration_crewai.py`

## Framework-Specific Integration

### LangGraph Integration

**What LangGraph provides**:
- Stateful graph execution with conditional edges
- Checkpointing and "time-travel" debugging
- Parallel node execution
- Built-in persistence

**What AAF adds**:
- REST API for LangGraph agents
- Memory systems for cross-session context
- Human-in-the-loop approvals
- Multi-framework orchestration
- Retry policies with exponential backoff

**Integration Code** (Using Built-in Adapter):

```python
from aaf import SequentialPattern, LangGraphAdapter  # Built-in!
from langgraph.prebuilt import create_react_agent

# Create LangGraph agent
lg_agent = create_react_agent(model, tools)

# Wrap with AAF's built-in adapter (no custom wrapper needed!)
wrapped = LangGraphAdapter("langgraph_agent", lg_agent)

# Use with AAF orchestration
pipeline = SequentialPattern(agents=[wrapped, other_agents])
result = pipeline.execute({"messages": [...]})
```

**That's it! No wrapper classes to write!**

### Microsoft Agent Framework Integration

**What Microsoft Agent Framework provides**:
- Multi-agent patterns (sequential, concurrent, handoff, group chat)
- MCP (Model Context Protocol) support
- A2A (Agent-to-Agent) communication
- .NET and Python support

**What AAF adds**:
- REST API layer
- Advanced memory management
- Task planning abstractions
- Guardrails and safety validation
- Deployment patterns

**Integration Code** (Using Built-in Adapter):

```python
from aaf import HierarchicalPattern, MicrosoftAgentAdapter  # Built-in!
from agent_framework import ChatAgent

# Create Microsoft agents
ms_manager = ChatAgent(...)
ms_worker = ChatAgent(...)

# Wrap with AAF's built-in adapter (zero boilerplate!)
wrapped_manager = MicrosoftAgentAdapter("manager", ms_manager)
wrapped_worker = MicrosoftAgentAdapter("worker", ms_worker)

# Use with AAF hierarchical pattern
hierarchy = HierarchicalPattern(
    manager_agent=wrapped_manager,
    worker_agents=[wrapped_worker]
)
result = hierarchy.execute({"task": "..."})
```

**Just one line per agent!**

### CrewAI Integration

**What CrewAI provides**:
- Role-based agent definition (role, goal, backstory)
- Crew and Flow orchestration
- Built-in task delegation
- 100+ built-in tools

**What AAF adds**:
- Memory systems
- Planning abstractions
- Guardrails and safety rules
- REST API exposure
- State persistence

**Integration Code** (Using Built-in Adapter):

```python
from aaf import CrewAIAdapter, SimpleTaskPlanner, GuardrailValidator  # Built-in!
from crewai import Agent

# Create CrewAI agents
researcher = Agent(role="Researcher", goal="...", backstory="...")
writer = Agent(role="Writer", goal="...", backstory="...")

# Wrap with AAF adapter (automatic!)
aaf_researcher = CrewAIAdapter("researcher", researcher)
aaf_writer = CrewAIAdapter("writer", writer)

# Add AAF features
planner = SimpleTaskPlanner()
plan = planner.create_plan("Research and write report", context={})

guardrails = GuardrailValidator(rules=[...])
if guardrails.validate(action):
    result = aaf_researcher.execute({"task": "research AI"})
```

**Built-in adapter handles all the protocol complexity!**

## Built-in Framework Adapters (Zero Boilerplate!)

AAF provides ready-to-use adapters for popular frameworks:

```python
from aaf import (
    LangGraphAdapter,      # For LangGraph agents
    MicrosoftAgentAdapter, # For Microsoft Agent Framework
    CrewAIAdapter,         # For CrewAI agents
    AutoGenAdapter         # For AutoGen agents
)

# Example: Wrap any framework agent in one line
langgraph_agent = LangGraphAdapter("researcher", your_lg_agent)
microsoft_agent = MicrosoftAgentAdapter("analyst", your_ms_agent)
crewai_agent = CrewAIAdapter("writer", your_crew_agent)

# All adapters follow the same pattern - no custom wrapper code needed!
```

**Benefits**:
- ✅ No custom wrapper classes
- ✅ Consistent interface across frameworks
- ✅ Maintained by AAF (automatic updates)
- ✅ Protocol compliance guaranteed

## Simplified API (No Protocol Complexity)

For users who don't want to deal with protocols and abstractions at all, use the simplified API:

```python
from aaf.simplified_api import (
    create_agent,
    create_memory,
    create_team,
    create_planner
)

# Simple agent creation
agent1 = create_agent("researcher")
agent2 = create_agent("writer")
agent3 = create_agent("editor")

# Simple memory
memory = create_memory(max_size=100)
memory.remember("User prefers technical details")
results = memory.recall("technical")

# Simple team
team = create_team([agent1, agent2, agent3], pattern="sequential")
result = team.execute({"task": "create report"})

# Simple planning
planner = create_planner()
steps = planner.plan("Research AI and write summary")
```

**No protocols, no abstractions - just simple functions!**

## Deployment Options

### 1. Standalone AAF (FastAPI Service)

Deploy AAF as a standalone REST API service:

```bash
# Run locally
python api.py

# Access Swagger UI
open http://localhost:5000/docs

# Call via HTTP
curl -X POST http://localhost:5000/agent/execute \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "my_agent", ...}'
```

### 2. AAF + LangGraph on AKS

Deploy both as microservices:

```yaml
# AAF deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aaf-orchestrator
spec:
  template:
    spec:
      containers:
      - name: aaf
        image: aaf:latest
        ports:
        - containerPort: 5000

---
# LangGraph deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-agents
spec:
  template:
    spec:
      containers:
      - name: langgraph
        image: langgraph-agents:latest
        ports:
        - containerPort: 8000
```

AAF calls LangGraph agents via HTTP/gRPC.

### 3. Embedded Integration

Embed AAF components directly in your application:

```python
# Your existing LangGraph application
from langgraph import ...
from aaf import InMemoryShortTermMemory, ApprovalWorkflow

# Add AAF memory to your LangGraph agent
memory = InMemoryShortTermMemory()
memory.add({"content": "Previous conversation context"})

# Add AAF approval workflow
approval = ApprovalWorkflow()
if approval.request("Execute sensitive operation"):
    # Run your LangGraph agent
    result = lg_agent.invoke(input)
```

## Choosing the Right Approach

| Scenario | Recommended Pattern |
|----------|---------------------|
| Need REST API for existing agents | Pattern 2: AAF as Infrastructure |
| Coordinating agents from multiple frameworks | Pattern 1: AAF as Orchestration |
| Want simple API without protocols | Use Simplified API |
| Need memory + HITL for LangGraph | Pattern 3: Hybrid |
| Multi-tenant SaaS with agents | AAF on AKS with multi-tenancy |
| Quick prototyping | Simplified API + Standalone deployment |
| Production enterprise system | Full AAF + AKS deployment |

## Best Practices

1. **Start Simple**: Use simplified API for prototyping
2. **Wrap, Don't Replace**: Keep existing framework agents, add AAF features
3. **Separate Concerns**: Use AAF for orchestration/infrastructure, frameworks for agent logic
4. **Leverage Strengths**: 
   - LangGraph for stateful workflows
   - Microsoft Agent Framework for enterprise features
   - CrewAI for role-based collaboration
   - AAF for REST API, memory, and production features
5. **Deploy Strategically**: Use AKS for scale, containers for portability

## Examples

| Example File | What It Shows |
|--------------|---------------|
| `examples/integration_langgraph.py` | AAF orchestrating LangGraph agents |
| `examples/integration_microsoft_agent.py` | AAF adding features to Microsoft agents |
| `examples/integration_crewai.py` | AAF providing guardrails for CrewAI |
| `examples/complete_example.py` | Pure AAF without other frameworks |

## Next Steps

1. Try the integration examples
2. Use the simplified API for quick starts
3. Deploy to AKS using the deployment guide
4. Read framework-specific documentation
5. Build your hybrid agentic system!

## Resources

- **AAF Documentation**: `USER_GUIDE.md`, `QUICKSTART.md`
- **Deployment**: `deployment/DEPLOYMENT_GUIDE.md`
- **LangGraph**: https://docs.langchain.com/langgraph
- **Microsoft Agent Framework**: https://learn.microsoft.com/agent-framework
- **CrewAI**: https://docs.crewai.com
