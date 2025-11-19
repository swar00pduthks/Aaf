# AAF + Pydantic AI: Best of Both Worlds

## The Perfect Combination

**AAF uses Pydantic AI as the foundation** and adds decorator simplicity + orchestration on top.

```python
from pydantic import BaseModel
from aaf import pydantic_agent, workflow, retry, validate

class ResearchOutput(BaseModel):
    summary: str
    findings: list[str]
    confidence: float

# Pydantic AI base + AAF decorators
@retry(max_attempts=3)
@validate(lambda r: r.confidence > 0.7)
@pydantic_agent(
    model="openai:gpt-4",
    result_type=ResearchOutput  # Type-safe!
)
def researcher(query: str):
    return query  # Pydantic AI handles the LLM call

# Orchestrate multiple providers
@pydantic_agent(model="openai:gpt-4")
def openai_agent(query): return query

@pydantic_agent(model="anthropic:claude-3-5-sonnet")
def anthropic_agent(query): return query

@pydantic_agent(model="gemini:gemini-2.0-flash")
def gemini_agent(query): return query

@workflow(openai_agent, anthropic_agent, gemini_agent, pattern="sequential")
def multi_provider_pipeline(query): pass
```

---

## What You Get

### From Pydantic AI (Foundation)

✅ **Type Safety** - Full Pydantic validation  
✅ **Multi-Provider** - 20+ LLMs (OpenAI, Anthropic, Gemini, Cohere, etc.)  
✅ **Streaming** - Real-time responses with validation  
✅ **Tool Registration** - `@agent.tool` decorator  
✅ **Dependency Injection** - Type-safe context passing  
✅ **Production Quality** - 100% test coverage  

### From AAF (Enhancement Layer)

✅ **Decorator Simplicity** - `@pydantic_agent`, `@workflow`, `@retry`, etc.  
✅ **Multi-Framework Orchestration** - Mix Pydantic AI + LangGraph + CrewAI  
✅ **Production Features** - Memory, HITL, guardrails, planning  
✅ **REST API Layer** - Expose agents as FastAPI services  
✅ **Zero Boilerplate** - No manual wrapper classes  

---

## Comparison

### Before (Manual Pydantic AI)

```python
from pydantic_ai import Agent as PydanticAgent
from pydantic import BaseModel

class Output(BaseModel):
    result: str

# Create agent manually
agent1 = PydanticAgent('openai:gpt-4', result_type=Output)
agent2 = PydanticAgent('anthropic:claude-3-5-sonnet', result_type=Output)

# Manual orchestration (60+ lines)
class Pipeline:
    def __init__(self):
        self.agent1 = agent1
        self.agent2 = agent2
    
    def execute(self, query):
        result1 = self.agent1.run_sync(query)
        result2 = self.agent2.run_sync(result1.data.result)
        return result2.data
    
    # + retry logic, validation, memory, etc. (more boilerplate)

pipeline = Pipeline()
result = pipeline.execute("my query")
```

### After (AAF + Pydantic AI)

```python
from aaf import pydantic_agent, workflow, retry, validate
from pydantic import BaseModel

class Output(BaseModel):
    result: str

# Create agents with decorators
@pydantic_agent(model="openai:gpt-4", result_type=Output)
def agent1(query): return query

@pydantic_agent(model="anthropic:claude-3-5-sonnet", result_type=Output)
def agent2(query): return query

# Auto-orchestrate
@retry(max_attempts=3)
@validate(lambda r: r is not None)
@workflow(agent1, agent2, pattern="sequential")
def pipeline(query): pass

result = pipeline("my query")
```

**95% less code!**

---

## Installation

```bash
# Install Pydantic AI
pip install pydantic-ai

# AAF automatically uses it when available
from aaf import pydantic_agent
```

---

## Use Cases

### 1. Type-Safe Research Agent

```python
from pydantic import BaseModel, Field
from aaf import pydantic_agent

class ResearchOutput(BaseModel):
    summary: str = Field(description="Brief summary")
    key_findings: list[str] = Field(description="Key findings")
    confidence: float = Field(ge=0, le=1)

@pydantic_agent(
    model="openai:gpt-4",
    result_type=ResearchOutput,
    instructions="You are a thorough research assistant"
)
def researcher(query: str):
    return query  # Pydantic AI handles everything

result = researcher("AI trends 2025")
print(result.summary)  # Type-safe access!
```

### 2. Multi-Provider Pipeline

```python
from aaf import pydantic_agent, workflow

@pydantic_agent(model="openai:gpt-4")
def research(query): return query

@pydantic_agent(model="anthropic:claude-3-5-sonnet")
def analyze(research): return research

@pydantic_agent(model="gemini:gemini-2.0-flash")
def write(analysis): return analysis

@workflow(research, analyze, write, pattern="sequential")
def content_pipeline(query): pass

result = content_pipeline("quantum computing")
```

### 3. Chatbot with Memory

```python
from aaf import chatbot, with_memory

@with_memory(key="chat_history")
@chatbot(model="anthropic:claude-3-5-sonnet")
def support_bot():
    """You are a helpful customer support agent."""
    pass

response1 = support_bot("Hello!")
response2 = support_bot("What can you help with?")  # Remembers context
```

### 4. Production-Ready Agent

```python
from aaf import (
    pydantic_agent, retry, requires_approval, 
    guardrail, with_memory, stack
)

production_stack = stack(
    retry(max_attempts=3),
    requires_approval(),
    with_memory(),
    guardrail(severity="high")
)

@production_stack
@pydantic_agent(model="openai:gpt-4", result_type=Output)
def production_agent(task):
    return task
```

### 5. Wrap Existing Pydantic AI Agents

```python
from pydantic_ai import Agent as PydanticAgent
from aaf import from_pydantic_ai, workflow

# Your existing Pydantic AI agent
existing_agent = PydanticAgent('openai:gpt-4', result_type=MyOutput)

# Wrap for AAF
aaf_agent = from_pydantic_ai(existing_agent, "my_agent")

# Use with AAF orchestration
@workflow(aaf_agent, other_agent, pattern="sequential")
def pipeline(query): pass
```

---

## Why This Matters

### Pydantic AI is Amazing For:
- Type-safe LLM interactions
- Multi-provider support
- Production-grade engineering

### But It Doesn't Have:
- ❌ Decorator-based simplicity
- ❌ Multi-framework orchestration
- ❌ Built-in memory/HITL/guardrails
- ❌ REST API layer

### AAF Fills These Gaps:
- ✅ Uses Pydantic AI as the foundation
- ✅ Adds decorator simplicity
- ✅ Adds orchestration
- ✅ Adds production features

---

## Positioning

**AAF is NOT replacing Pydantic AI** - it's **enhancing** it!

- Use Pydantic AI directly: For simple single-agent use cases
- Use AAF with Pydantic AI: For multi-agent systems with orchestration

**AAF = Pydantic AI + Decorators + Orchestration + Production Features**

---

## Migration Path

### If You're Using Pydantic AI Already:

```python
# Before
from pydantic_ai import Agent
agent = Agent('openai:gpt-4', result_type=Output)

# After - just add decorator!
from aaf import pydantic_agent

@pydantic_agent(model="openai:gpt-4", result_type=Output)
def agent(query): return query

# Or wrap existing agent
from aaf import from_pydantic_ai
aaf_agent = from_pydantic_ai(agent, "my_agent")
```

### If You're New to Both:

```python
# Start with AAF - it uses Pydantic AI automatically
from aaf import pydantic_agent, workflow
from pydantic import BaseModel

class Output(BaseModel):
    result: str

@pydantic_agent(model="openai:gpt-4", result_type=Output)
def my_agent(query): return query

# You get everything: type safety + simplicity + orchestration
```

---

## Conclusion

**Best of both worlds:**
- Pydantic AI's engineering excellence
- AAF's decorator simplicity
- Perfect combination for production agentic systems

**AAF doesn't compete with Pydantic AI - it complements it!**
