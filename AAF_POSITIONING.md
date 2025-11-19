## **AAF's Unique Value: Zero-Boilerplate Decorators**

### **The Problem AAF Solves**

You have agents from different frameworks (LangGraph, CrewAI, Microsoft), and you need to:
1. ❌ **Orchestrate them together** - without writing adapter classes
2. ❌ **Reduce boilerplate** - no manual protocol implementations  
3. ❌ **Keep it simple** - Lambda-like decorator syntax

### **AAF's Solution: Just Decorate**

```python
from aaf import agent, workflow, langgraph_agent

# Turn ANY function into an agent - zero boilerplate!
@agent
def researcher(query: str) -> str:
    return search_and_analyze(query)

@langgraph_agent
def my_lg_agent(messages):
    return langgraph_instance.invoke(messages)

# Auto-orchestrate with one decorator!
@workflow(researcher, my_lg_agent, pattern="sequential")
def pipeline(query: str):
    pass  # That's it - fully orchestrated!
```

**That's AAF's standout: Lambda-like simplicity for multi-agent systems.**

---

## **Comparison with Other Frameworks**

### **vs. Pydantic AI**

| Feature | Pydantic AI | AAF |
|---------|-------------|-----|
| **Single Agent DX** | ✅ Best-in-class | ⚠️ Use Pydantic AI |
| **Type Safety** | ✅ Full | ⚠️ Optional (EnhancedAgent) |
| **Multi-Provider** | ✅ 20+ | ⚠️ Optional |
| **Decorators for ANY framework** | ❌ | ✅ **UNIQUE** |
| **Multi-agent orchestration** | ❌ | ✅ **UNIQUE** |
| **Zero-boilerplate wrappers** | ❌ | ✅ **UNIQUE** |

**When to use AAF**: You need to orchestrate agents from **multiple frameworks**  
**When to use Pydantic AI**: You're building a **single new agent** with type safety

### **vs. LangGraph**

| Feature | LangGraph | AAF |
|---------|-----------|-----|
| **Stateful workflows** | ✅ Best-in-class | ⚠️ Use LangGraph |
| **Graph execution** | ✅ Advanced | ⚠️ Use LangGraph |
| **Wrap ANY framework** | ❌ | ✅ **UNIQUE** |
| **One-decorator orchestration** | ❌ | ✅ **UNIQUE** |
| **Multi-framework pipelines** | ❌ | ✅ **UNIQUE** |

**When to use AAF**: Wrap LangGraph agents and orchestrate with others  
**When to use LangGraph**: Complex stateful workflows within one framework

### **vs. CrewAI**

| Feature | CrewAI | AAF |
|---------|--------|-----|
| **Role-based agents** | ✅ Best-in-class | ⚠️ Use CrewAI |
| **Crew patterns** | ✅ Native | ⚠️ Use CrewAI |
| **Wrap ANY framework** | ❌ | ✅ **UNIQUE** |
| **Decorator simplicity** | ❌ | ✅ **UNIQUE** |
| **Mix CrewAI + LangGraph + others** | ❌ | ✅ **UNIQUE** |

**When to use AAF**: Wrap CrewAI crews and orchestrate with other frameworks  
**When to use CrewAI**: Pure role-based collaboration within one framework

---

## **AAF's Architecture**

### **Three Layers**

```
┌─────────────────────────────────────────────────┐
│  Layer 1: Zero-Boilerplate Decorators          │
│  @agent, @workflow, @langgraph_agent            │  ← AAF's STANDOUT
├─────────────────────────────────────────────────┤
│  Layer 2: Framework Adapters (Optional)        │
│  LangGraphAdapter, CrewAIAdapter, etc.          │  ← If you need control
├─────────────────────────────────────────────────┤
│  Layer 3: Production Features                  │
│  Memory, Planning, HITL, REST API              │  ← AAF's value-adds
└─────────────────────────────────────────────────┘
```

**Most users only need Layer 1!**

### **Optional: Type-Safe Agents**

If you want Pydantic AI-like type safety **within AAF**:

```python
from aaf import EnhancedAgent
from pydantic import BaseModel

class Output(BaseModel):
    result: str
    confidence: float

agent = EnhancedAgent(
    agent_id="researcher",
    model="openai:gpt-4",
    result_type=Output  # Type-safe
)
```

**But this is optional** - AAF's core value is the decorator-based orchestration.

---

## **Real-World Example**

**Before AAF (100+ lines of boilerplate):**

```python
# Wrap LangGraph agent
class LangGraphWrapper:
    def __init__(self, lg_agent):
        self._agent = lg_agent
    @property
    def agent_id(self): return "lg"
    def execute(self, input_data):
        return self._agent.invoke(input_data)
    def initialize(self, config): pass
    def shutdown(self): pass

# Wrap CrewAI agent
class CrewAIWrapper:
    def __init__(self, crew):
        self._crew = crew
    @property
    def agent_id(self): return "crew"
    def execute(self, input_data):
        return self._crew.kickoff()
    def initialize(self, config): pass
    def shutdown(self): pass

# Manual orchestration
from aaf import SequentialPattern
lg_wrapped = LangGraphWrapper(lg_agent)
crew_wrapped = CrewAIWrapper(crew)
pipeline = SequentialPattern(agents=[lg_wrapped, crew_wrapped])
result = pipeline.execute(...)
```

**After AAF (4 lines):**

```python
from aaf import langgraph_agent, crewai_agent, workflow

@langgraph_agent
def lg_agent(messages): return langgraph_instance.invoke(messages)

@crewai_agent
def crew_agent(task): return crew.kickoff()

@workflow(lg_agent, crew_agent, pattern="sequential")
def pipeline(query): pass

result = pipeline("my query")
```

**97% less boilerplate!**

---

## **Positioning Statement**

**"AAF: The simplest way to orchestrate agents from any framework"**

- ✅ Wrap LangGraph, CrewAI, Microsoft, Pydantic AI, or custom functions
- ✅ One decorator = production-ready agent
- ✅ Auto-orchestration with @workflow
- ✅ Lambda-like simplicity
- ✅ Optional type safety if you need it
- ✅ Optional REST API, memory, planning

**AAF is NOT**:
- ❌ A replacement for Pydantic AI (use Pydantic AI for new agents)
- ❌ A replacement for LangGraph (use LangGraph for stateful workflows)
- ❌ Another agent framework

**AAF IS**:
- ✅ The glue between frameworks
- ✅ The simplest orchestration layer
- ✅ Zero-boilerplate agent creation

---

## **Target Users**

1. **Teams using multiple frameworks** - You have LangGraph, CrewAI, and custom agents
2. **Boilerplate haters** - You want Lambda-like simplicity
3. **Polyglot agent systems** - Mix and match any framework
4. **Production teams** - Need REST API, memory, guardrails on top of existing agents

---

## **Tagline**

**"Lambda for AI Agents - Just Decorate and Orchestrate"**
