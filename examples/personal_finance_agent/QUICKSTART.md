# Personal Finance Agent - Quick Start

## 🚀 Run in 30 Seconds

```bash
# Test the agent
python examples/personal_finance_agent/finance_agent.py

# Or run the API server
python examples/personal_finance_agent/finance_api.py
```

## 💬 Try It Now

### Option 1: Command Line (Instant)

```bash
python examples/personal_finance_agent/finance_agent.py
```

You'll see:
- ✅ Track expense example
- 📊 Spending summary
- 💡 Budget advice
- 📈 Investment recommendations (A2A delegation)

### Option 2: API Server

```bash
# Start server
python examples/personal_finance_agent/finance_api.py

# In another terminal, test it:
curl -X POST http://localhost:5001/finance/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I spent $50 on groceries"}'
```

### Option 3: CopilotKit UI (React)

**1. Install CopilotKit:**
```bash
npm install @copilotkit/react-core @copilotkit/react-ui
```

**2. Add to your React app:**
```tsx
import { CopilotKit } from '@copilotkit/react-core';
import { CopilotSidebar } from '@copilotkit/react-ui';

function App() {
  return (
    <CopilotKit runtimeUrl="http://localhost:5001/api/copilotkit">
      <YourApp />
      <CopilotSidebar defaultOpen={true} />
    </CopilotKit>
  );
}
```

**3. Start server + React app:**
```bash
# Terminal 1: Start finance API
python examples/personal_finance_agent/finance_api.py

# Terminal 2: Start React app
npm run dev
```

**Done!** Chat interface appears with your finance agent! 🎉

## 🎯 What You Can Ask

```
💰 Track Expenses:
"I spent $45.99 at Whole Foods"
"Paid $1500 for rent"

💵 Track Income:
"My salary was $5000 this month"
"Got $200 bonus"

📊 View Summary:
"Show me my spending summary"
"How much did I spend this month?"

💡 Budget Advice:
"How can I save more money?"
"Give me budget recommendations"

📈 Investment Advice (A2A):
"What should I invest in?"
"How should I allocate my portfolio?"
```

## 🏗️ How It Works

### MCP Tools
```python
@node
@mcp_tool("transaction_tracker")
def track_expense(state):
    # Stores transaction in database via MCP server
    pass
```

### A2A Delegation
```python
@node
def delegate_to_investment_agent(state):
    # Calls specialist investment advisor agent
    # In production: a2a_client.delegate("investment_advisor", profile)
    pass
```

### Autonomous Agents
```python
@node
@autonomous_agent(model="openai:gpt-4", tools=["budget_analyzer"], memory=True)
def get_budget_advice(state):
    # Agent uses tools and memory for personalized advice
    pass
```

### Workflow Orchestration
```python
@workflow_graph(
    start="parse_intent",
    routing={
        "parse_intent": lambda s: route_by_intent(s),
        "track_expense": "END",
        "invest_advice": "delegate_to_investment_agent"
    }
)
def personal_finance_agent(user_query: str):
    return {"user_query": user_query}
```

## 📚 Full Documentation

See [README.md](./README.md) for:
- Complete API reference
- Production deployment guide
- Database setup
- Authentication
- More examples

## 🎉 That's It!

You now have a working personal finance agent with:
- ✅ MCP tool integration
- ✅ A2A protocol delegation
- ✅ Autonomous agents
- ✅ CopilotKit UI (optional)

**All powered by AAF!** 🚀
