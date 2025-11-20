# Personal Finance Assistant (AAF Example)

A complete production-ready example demonstrating AAF's capabilities with a real-world use case.

## Features

### 💰 Financial Tracking
- **Expense Tracking** - Log purchases with automatic categorization
- **Income Tracking** - Record salary, bonuses, side income
- **Transaction History** - View all financial activity

### 📊 Analysis & Insights
- **Spending Summary** - Monthly breakdown by category
- **Budget Analysis** - Compare to recommended allocations (50/30/20 rule)
- **Savings Calculator** - Identify money-saving opportunities

### 💡 Recommendations
- **Budget Advice** - Personalized tips to reduce spending
- **Investment Suggestions** - Portfolio recommendations via A2A delegation
- **Savings Plans** - Automated savings strategies

## Architecture

This example showcases:

### ✅ MCP Tool Integration
```python
@node
@mcp_tool("transaction_tracker")
def track_expense(state):
    # Calls MCP server to store transaction in database
    pass
```

### ✅ A2A Protocol
```python
@node
def delegate_to_investment_agent(state):
    # Delegates to specialized investment advisor agent
    # In production: a2a_client.delegate("investment_advisor", profile)
    pass
```

### ✅ Autonomous Agents
```python
@node
@autonomous_agent(
    model="openai:gpt-4",
    tools=["transaction_query", "budget_analyzer"],
    memory=True
)
def get_budget_advice(state):
    # Agent uses tools and memory to provide personalized advice
    pass
```

### ✅ Workflow Orchestration
```python
@workflow_graph(
    start="parse_intent",
    routing={
        "parse_intent": lambda s: {
            "track_expense": "track_expense",
            "view_summary": "view_summary",
            "invest_advice": "delegate_to_investment_agent"
        }[s["intent"]]
    }
)
def personal_finance_agent(user_query: str):
    return {"user_query": user_query}
```

## Quick Start

### Option 1: Run Demo (No Setup Required)

```bash
python examples/personal_finance_agent/finance_agent.py
```

Output:
```
======================================================================
Personal Financial Assistant (AAF Demo)
======================================================================

Example 1: Track Expense
✅ Logged expense: $45.99 for food

Example 2: View Summary
📊 Financial Summary
Income: $5,000.00
Expenses: $3,245.67
Savings: $1,754.33 (35.1%)

Example 3: Budget Advice
💡 Budget Recommendations
...

Example 4: Investment Advice (A2A Delegation)
📈 Investment Recommendations (via Investment Advisor Agent)
...
```

### Option 2: Run API Server

```bash
python examples/personal_finance_agent/finance_api.py
```

Then test:
```bash
# Chat with agent
curl -X POST http://localhost:5001/finance/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I spent $50 on groceries"}'

# Get summary
curl http://localhost:5001/finance/summary

# View examples
curl http://localhost:5001/finance/demo
```

### Option 3: Use with CopilotKit

**Install CopilotKit:**
```bash
npm install @copilotkit/react-core @copilotkit/react-ui
```

**Add to your React app:**
```tsx
import { CopilotKit } from '@copilotkit/react-core';
import { CopilotSidebar } from '@copilotkit/react-ui';

function FinanceApp() {
  return (
    <CopilotKit 
      runtimeUrl="http://localhost:5001/api/copilotkit"
      agent="finance_assistant"
    >
      <YourApp />
      <CopilotSidebar 
        defaultOpen={true}
        labels={{
          title: "Finance Assistant",
          initial: "Track expenses, get budget tips, investment advice!"
        }}
      />
    </CopilotKit>
  );
}
```

## Example Conversations

### Track Expense
```
User: I spent $45.99 at Whole Foods
Agent: ✅ Logged expense: $45.99 for food
      Category: Groceries
      Date: 2024-11-20
```

### View Summary
```
User: Show me my spending summary
Agent: 📊 Financial Summary

       Income: $5,000.00
       Expenses: $3,245.67
       Savings: $1,754.33 (35.1%)

       Top Spending Categories:
       • Rent: $1,500.00 (46.2%)
       • Food: $890.50 (27.4%)
       • Entertainment: $509.97 (15.7%)
       • Transport: $345.20 (10.6%)
```

### Budget Advice
```
User: How can I save more money?
Agent: 💡 Budget Recommendations

       Current Allocation:
       • Needs: 65% (target: 50%)
       • Wants: 20% (target: 30%)
       • Savings: 15% (target: 20%)

       Action Items:

       1. Food Spending - Save $240.50/month
          • Meal prep on Sundays
          • Use grocery list
          • Shop at discount stores

       2. Entertainment - Save $209.97/month
          • Share streaming subscriptions
          • Look for free local events
          • Use library for books/movies

       💰 Total Potential Savings: $450.47/month
```

### Investment Advice
```
User: What should I invest in?
Agent: 📈 Investment Recommendations (via Investment Advisor Agent)

       Recommended Asset Allocation:
       • Stocks: 60%
       • Bonds: 30%
       • Cash: 10%

       Specific Investments:
       • Index Fund (VTI)
         - Allocate: 40%
         - Why: Low-cost total market exposure

       • International Fund (VXUS)
         - Allocate: 20%
         - Why: Geographic diversification

       • Bond Fund (BND)
         - Allocate: 30%
         - Why: Stability and income

       💸 Monthly Investment: $1,400.00

       Projected Portfolio Value:
       • 5 years: $98,500.00
       • 10 years: $235,000.00
       • 20 years: $687,000.00
```

## Production Deployment

### 1. Connect Real MCP Server

Replace simulated MCP calls with real database operations:

```python
# Install MCP SDK
pip install mcp-sdk

# Configure MCP server
from mcp import MCPClient

mcp_client = MCPClient("http://your-mcp-server:8080")

@node
@mcp_tool("transaction_tracker")
def track_expense(state):
    # Real MCP call
    result = mcp_client.call_tool("transaction_tracker", {
        "amount": extract_amount(state["user_query"]),
        "category": extract_category(state["user_query"]),
        "date": datetime.now()
    })
    return {"response": result}
```

### 2. Deploy Investment Agent

Create separate A2A-compatible agent for investments:

```python
# investment_agent_server.py
from aaf import a2a_server

@a2a_server.register("investment_advisor")
def investment_advisor(user_profile):
    # Real investment analysis logic
    return recommendations
```

### 3. Add Authentication

```python
from fastapi import Depends
from aaf.auth import get_current_user

@app.post("/finance/chat")
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    # User-specific financial data
    result = personal_finance_agent(request.message, user_id=user.id)
    return result
```

### 4. Database Setup

```sql
-- Create tables for financial data
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    type VARCHAR(10), -- 'income' or 'expense'
    amount DECIMAL(10, 2),
    category VARCHAR(50),
    description TEXT,
    date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE budgets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    category VARCHAR(50),
    monthly_limit DECIMAL(10, 2)
);
```

## Tech Stack

- **AAF Framework** - Workflow orchestration
- **FastAPI** - HTTP API
- **MCP Protocol** - Database operations
- **A2A Protocol** - Agent delegation
- **CopilotKit** - Beautiful UI (optional)
- **PostgreSQL** - Data storage (production)

## File Structure

```
examples/personal_finance_agent/
├── README.md                 # This file
├── finance_agent.py          # Main agent workflow
├── finance_api.py            # FastAPI server
└── requirements.txt          # Python dependencies
```

## Next Steps

1. **Connect to real database** - Replace simulated data with PostgreSQL
2. **Deploy investment agent** - Set up separate A2A service
3. **Add authentication** - User accounts and profiles
4. **Build frontend** - React app with CopilotKit
5. **Add more features** - Bill reminders, savings goals, debt tracking

## Learn More

- [AAF Documentation](../../replit.md)
- [MCP Protocol](https://modelcontextprotocol.io)
- [A2A Protocol](https://a2a-protocol.org)
- [CopilotKit](https://docs.copilotkit.ai)

---

**Built with AAF** - Production-ready agentic application framework 🚀
