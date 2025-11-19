# AAF's Decorator Philosophy: Lambda-Like Simplicity for Everything

## The Vision

**"If AWS Lambda simplified serverless functions, AAF simplifies agentic applications"**

Just add a decorator - no boilerplate, no complexity, production-ready instantly.

---

## Core Principle

### Everything is a Decorator

```python
from aaf import (
    agent,                  # Create agents
    workflow,               # Orchestrate
    validate,               # Add validation
    requires_approval,      # Add HITL
    with_memory,           # Add memory
    retry,                 # Add retry logic
    guardrail,             # Add safety
    plan_task,             # Add planning
    stack                  # Compose everything
)

# Start simple
@agent
def researcher(query): return search(query)

# Add features incrementally
@with_memory()
@agent
def smart_researcher(query): return search(query)

# Stack everything for production
@stack(
    retry(max_attempts=3),
    requires_approval(),
    with_memory(),
    guardrail(severity="high"),
    validate(lambda r: r is not None)
)
@agent
def production_researcher(query): return search(query)
```

**That's the philosophy: Start simple, add complexity as decorators.**

---

## Complete Decorator Catalog

### 1. Agent Creation Decorators

```python
@agent                          # Any function → agent
@langgraph_agent               # LangGraph wrapper
@crewai_agent                  # CrewAI wrapper  
@microsoft_agent               # Microsoft Agent Framework wrapper
```

### 2. Orchestration Decorators

```python
@workflow(agent1, agent2, pattern="sequential")     # Auto-orchestrate
@workflow(manager, *workers, pattern="hierarchical") # Manager-worker
```

### 3. Validation Decorators

```python
@validate(rule1, rule2, ...)           # Custom validation rules
@guardrail(severity="high")            # Safety guardrails
@no_bulk_operations(max_count=100)     # Prevent bulk ops
```

### 4. Human-in-the-Loop Decorators

```python
@requires_approval(message="...")      # Request approval before exec
@human_feedback()                       # Request feedback after exec
```

### 5. Memory Decorators

```python
@with_memory(key="context")            # Auto-remember past calls
```

### 6. Reliability Decorators

```python
@retry(max_attempts=3, delay=1.0)      # Auto-retry with backoff
```

### 7. Planning Decorators

```python
@plan_task(available_tools=[...])      # Auto-create execution plan
```

### 8. Observability Decorators

```python
@log_execution(level="INFO")           # Auto-log execution
```

### 9. Composition Decorator

```python
@stack(*decorators)                    # Stack multiple decorators
```

---

## Real-World Examples

### Example 1: Simple Function → Production Agent (3 lines)

```python
# Before AAF (100+ lines of boilerplate)
class MyAgent:
    def __init__(self): ...
    def execute(self, input_data): ...
    def initialize(self, config): ...
    def shutdown(self): ...
    # + wrapper classes, manual retry, manual validation, etc.

# After AAF (3 lines)
@retry(max_attempts=3)
@requires_approval()
@agent
def my_agent(query): return process(query)
```

**97% less code!**

### Example 2: Multi-Framework Orchestration (4 lines)

```python
@langgraph_agent
def lg(msgs): return langgraph_instance.invoke(msgs)

@crewai_agent
def crew(task): return crew_instance.kickoff()

@workflow(lg, crew, pattern="sequential")
def pipeline(query): pass

result = pipeline("my query")
```

### Example 3: Production-Ready Agent (1 decorator stack)

```python
production_stack = stack(
    retry(max_attempts=3),
    requires_approval(),
    with_memory(),
    guardrail(severity="high"),
    validate(lambda r: r is not None),
    log_execution()
)

@production_stack
@agent
def production_agent(task): return execute(task)
```

**All production features in one decorator!**

---

## Comparison with Other Approaches

### AAF's Decorator Approach

```python
@validate(confidence_check)
@retry(max_attempts=3)
@with_memory()
@agent
def my_agent(query):
    return process(query)
```

**4 lines, fully featured**

### Manual Approach (No Framework)

```python
class MyAgent:
    def __init__(self):
        self.memory = Memory()
        self.validator = Validator(rules=[confidence_check])
        self.retry_policy = RetryPolicy(max_attempts=3)
    
    def execute(self, input_data):
        for attempt in range(self.retry_policy.max_attempts):
            try:
                # Load memory
                context = self.memory.load()
                
                # Execute
                result = self._process(input_data, context)
                
                # Validate
                if not self.validator.validate(result):
                    raise ValidationError()
                
                # Store in memory
                self.memory.save(result)
                
                return result
            except Exception as e:
                if attempt == self.retry_policy.max_attempts - 1:
                    raise
                time.sleep(self.retry_policy.delay)
    
    def _process(self, input_data, context):
        # Your logic here
        pass
```

**60+ lines, error-prone, hard to maintain**

---

## Philosophy in Action

### Start Simple

```python
@agent
def researcher(query):
    return search_and_analyze(query)
```

### Add Features Incrementally

```python
# Week 1: Add validation
@validate(lambda r: len(r) > 10)
@agent
def researcher(query): ...

# Week 2: Add retry
@retry(max_attempts=3)
@validate(lambda r: len(r) > 10)
@agent
def researcher(query): ...

# Week 3: Add approval for sensitive queries
@requires_approval()
@retry(max_attempts=3)
@validate(lambda r: len(r) > 10)
@agent
def researcher(query): ...
```

### Refactor to Stack

```python
research_stack = stack(
    requires_approval(),
    retry(max_attempts=3),
    validate(lambda r: len(r) > 10)
)

@research_stack
@agent
def researcher(query): ...
```

---

## Design Principles

1. **Composability** - Stack decorators freely
2. **Zero Boilerplate** - No wrapper classes, no manual setup
3. **Progressive Enhancement** - Start simple, add complexity as needed
4. **Framework Agnostic** - Works with any framework (LangGraph, CrewAI, etc.)
5. **Production Ready** - All features available as decorators

---

## What Makes This Unique

### vs. Pydantic AI
- **Pydantic AI**: Type-safe single agents
- **AAF**: Multi-agent orchestration with decorators

### vs. LangGraph
- **LangGraph**: Stateful graph workflows
- **AAF**: Decorator-based simplicity

### vs. CrewAI
- **CrewAI**: Role-based collaboration
- **AAF**: Universal orchestration layer

**AAF is the only framework where EVERYTHING is a decorator.**

---

## AAF's Complete Value Proposition

```
┌─────────────────────────────────────────────────┐
│  Decorator-Based Simplicity (UNIQUE)            │
│  - @agent, @workflow, @validate, @retry, etc.   │
├─────────────────────────────────────────────────┤
│  Multi-Framework Orchestration (UNIQUE)         │
│  - LangGraph + CrewAI + Microsoft + Custom      │
├─────────────────────────────────────────────────┤
│  Production Features (UNIQUE combination)       │
│  - Memory + Planning + HITL + Guardrails        │
├─────────────────────────────────────────────────┤
│  Optional: Pydantic AI-like Type Safety         │
│  - EnhancedAgent with result_type validation    │
└─────────────────────────────────────────────────┘
```

---

## Tagline

**"Lambda for AI Agents - Just Decorate"**

- ✅ Zero boilerplate
- ✅ Production-ready features as decorators
- ✅ Works with any framework
- ✅ Progressive enhancement
- ✅ Stack everything

**AAF: The simplest way to build production agentic applications.**
