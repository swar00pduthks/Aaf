# Personal Finance Agent - Architecture Overview

## 🎯 What This Example Shows

A **production-ready personal finance assistant** demonstrating all AAF capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                   USER INTERACTIONS                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  "I spent $50 on groceries"        → Track Expense         │
│  "Show me my spending summary"     → View Summary          │
│  "How can I save more money?"      → Budget Advice         │
│  "What should I invest in?"        → Investment Advice     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 WORKFLOW ORCHESTRATION                      │
│                  (AAF Framework)                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐                                          │
│  │ Parse Intent │ ← Determines what user wants             │
│  └──────┬───────┘                                          │
│         │                                                   │
│    ┌────┴────┐                                             │
│    │ Routing │ ← Conditional routing to appropriate node   │
│    └────┬────┘                                             │
│         │                                                   │
│    ┌────┴────────────────────────────┐                     │
│    │                                 │                     │
│    ▼                                 ▼                     │
│  MCP Tools              Autonomous Agents        A2A       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Architecture Diagram

```
                    ┌─────────────────────┐
                    │   User Query        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Parse Intent Node   │
                    │  (@node + @llm)      │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Conditional Router  │
                    └──┬────┬────┬────┬───┘
                       │    │    │    │
        ┌──────────────┘    │    │    └──────────────┐
        │                   │    │                    │
        ▼                   ▼    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│ Track Expense │  │  View Summary   │  │ Investment Advice    │
│  (MCP Tool)   │  │ (Auto Agent +   │  │  (A2A Delegation)    │
│               │  │  Memory + Tools)│  │                      │
└───────────────┘  └─────────────────┘  └──────────────────────┘
        │                   │                         │
        │                   │                         │
        ▼                   ▼                         ▼
┌───────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│   Database    │  │  Budget Advice  │  │ Investment Advisor   │
│ (PostgreSQL)  │  │ (Auto Agent)    │  │ Agent (Remote A2A)   │
└───────────────┘  └─────────────────┘  └──────────────────────┘
```

## 🔧 Technology Stack

### AAF Features Used

| Feature | Where Used | Purpose |
|---------|------------|---------|
| **@node** | All functions | Define workflow steps |
| **@workflow_graph** | main function | Orchestrate nodes with routing |
| **@llm** | parse_intent | Simple LLM call for intent detection |
| **@mcp_tool** | track_expense, track_income | Database operations via MCP |
| **@autonomous_agent** | view_summary, get_budget_advice | Complex tasks with tools + memory |
| **A2A delegation** | delegate_to_investment_agent | Call specialist agent |

### External Integrations

```
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRATIONS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MCP Server          →  Transaction tracking database      │
│  A2A Protocol        →  Investment advisor agent           │
│  CopilotKit          →  Beautiful chat UI (optional)       │
│  PostgreSQL          →  Persistent storage                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Code Structure

```python
# Node 1: Intent parsing
@node
@llm(model="openai:gpt-4")
def parse_intent(state):
    # Classify user intent
    return {"intent": "track_expense"}

# Node 2a: MCP tool for expense tracking
@node
@mcp_tool("transaction_tracker")
def track_expense(state):
    # Call MCP server to store in database
    return {"response": "Logged expense"}

# Node 2b: Autonomous agent for analysis
@node
@autonomous_agent(
    model="openai:gpt-4",
    tools=["transaction_query", "budget_analyzer"],
    memory=True
)
def get_budget_advice(state):
    # Agent uses tools and memory
    return {"response": "Budget recommendations"}

# Node 2c: A2A delegation
@node
def delegate_to_investment_agent(state):
    # Call remote investment advisor agent
    return {"response": "Investment advice"}

# Workflow: Orchestrate everything
@workflow_graph(
    start="parse_intent",
    routing={
        "parse_intent": lambda s: route_by_intent(s),
        "track_expense": "END",
        "get_budget_advice": "END",
        "delegate_to_investment_agent": "END"
    }
)
def personal_finance_agent(user_query):
    return {"user_query": user_query}
```

## 🌊 Data Flow Examples

### Example 1: Track Expense (MCP Tool)

```
User: "I spent $50 on groceries"
    │
    ▼
Parse Intent → intent = "track_expense"
    │
    ▼
Track Expense Node (@mcp_tool)
    │
    ├─ Extract amount: $50
    ├─ Extract category: groceries
    ├─ Call MCP server: transaction_tracker
    │   └─ Store in PostgreSQL
    │
    ▼
Response: "✅ Logged expense: $50 for groceries"
```

### Example 2: Budget Advice (Autonomous Agent)

```
User: "How can I save more money?"
    │
    ▼
Parse Intent → intent = "get_budget_advice"
    │
    ▼
Budget Advice Node (@autonomous_agent)
    │
    ├─ Tool 1: Query transactions
    ├─ Tool 2: Analyze spending patterns
    ├─ Tool 3: Calculate savings potential
    ├─ Memory: Remember user preferences
    │
    ▼
Response: "💡 Budget Recommendations
           - Food: Save $240/month
           - Entertainment: Save $210/month"
```

### Example 3: Investment Advice (A2A Delegation)

```
User: "What should I invest in?"
    │
    ▼
Parse Intent → intent = "invest_advice"
    │
    ▼
Delegate to Investment Agent Node
    │
    ├─ Prepare user profile
    │   ├─ Age: 32
    │   ├─ Savings: $1,754/month
    │   └─ Risk tolerance: moderate
    │
    ├─ A2A Call to "investment_advisor_agent"
    │   └─ Remote agent analyzes profile
    │
    ▼
Response: "📈 Investment Recommendations
           - Stocks: 60% (VTI, VXUS)
           - Bonds: 30% (BND)
           - Cash: 10% (HYSA)"
```

## 🚀 Deployment Options

### Option 1: Standalone API

```bash
python finance_api.py
# Access at http://localhost:5001
```

### Option 2: CopilotKit Integration

```tsx
<CopilotKit runtimeUrl="http://localhost:5001/api/copilotkit">
  <FinanceApp />
  <CopilotSidebar />
</CopilotKit>
```

### Option 3: Mobile App

```python
# Expose REST API
from finance_api import app

# Mobile app hits:
# POST /finance/chat
# GET /finance/summary
```

## 📦 Files

```
examples/personal_finance_agent/
├── OVERVIEW.md          ← This file (architecture)
├── QUICKSTART.md        ← 30-second setup guide
├── README.md            ← Complete documentation
├── finance_agent.py     ← Main agent workflow
├── finance_api.py       ← FastAPI server
└── requirements.txt     ← Python dependencies
```

## 🎯 Key Takeaways

1. **MCP Tools** - Database operations, transaction tracking
2. **A2A Protocol** - Delegate to specialist agents
3. **Autonomous Agents** - Complex analysis with tools + memory
4. **Workflow Orchestration** - Conditional routing, clean architecture
5. **Production-Ready** - FastAPI, CopilotKit, authentication ready

## 🔗 Learn More

- [Quick Start Guide](./QUICKSTART.md) - Get running in 30 seconds
- [Complete Documentation](./README.md) - Full API reference
- [AAF Framework Docs](../../replit.md) - Framework overview

---

**Built with AAF** - Production-ready agentic applications 🚀
