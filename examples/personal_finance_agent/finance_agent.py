"""
Personal Financial Assistant Agent

A complete AAF example demonstrating:
- MCP tool integration (transaction tracking, budget analysis)
- A2A protocol (delegating to investment advisor agent)
- Node-based workflow orchestration
- Database storage for financial data
- CopilotKit UI integration

Features:
- Track income and expenses
- Categorize spending
- Budget management
- Savings recommendations
- Investment suggestions via A2A delegation
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

from aaf import node, workflow_graph, llm, mcp_tool, autonomous_agent
from typing import Dict, Any
import json
from datetime import datetime


# ============================================================================
# Node 1: Parse User Intent
# ============================================================================

@node
@llm(model="openai:gpt-4")
def parse_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine what the user wants to do with their finances.
    
    Intents:
    - track_expense: Log a new expense
    - track_income: Log salary/income
    - view_summary: See spending summary
    - get_budget_advice: Get budget recommendations
    - invest_advice: Get investment suggestions (delegates to A2A)
    """
    user_query = state.get("user_query", "")
    
    # Simple intent classification (in production, use actual LLM)
    if any(word in user_query.lower() for word in ["spent", "bought", "paid", "expense"]):
        intent = "track_expense"
    elif any(word in user_query.lower() for word in ["salary", "income", "earned", "paycheck"]):
        intent = "track_income"
    elif any(word in user_query.lower() for word in ["summary", "total", "how much", "spending"]):
        intent = "view_summary"
    elif any(word in user_query.lower() for word in ["budget", "save", "savings"]):
        intent = "get_budget_advice"
    elif any(word in user_query.lower() for word in ["invest", "investment", "stocks", "portfolio"]):
        intent = "invest_advice"
    else:
        intent = "view_summary"
    
    return {
        **state,
        "intent": intent,
        "parsed_query": user_query
    }


# ============================================================================
# Node 2a: Track Expense (MCP Tool)
# ============================================================================

@node
@mcp_tool("transaction_tracker")
def track_expense(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use MCP tool to log expense in database.
    
    In production, this would call a real MCP server that:
    - Parses transaction details from user query
    - Stores in PostgreSQL database
    - Categorizes transaction (food, transport, entertainment, etc.)
    """
    # Simulated MCP tool call
    transaction = {
        "type": "expense",
        "amount": 45.99,  # Would be extracted from user_query
        "category": "food",
        "description": "Grocery shopping",
        "date": datetime.now().isoformat(),
        "merchant": "Whole Foods"
    }
    
    # In production: mcp_client.call_tool("transaction_tracker", transaction)
    
    return {
        **state,
        "response": {
            "type": "transaction_logged",
            "message": f"✅ Logged expense: ${transaction['amount']} for {transaction['category']}",
            "transaction": transaction
        }
    }


# ============================================================================
# Node 2b: Track Income (MCP Tool)
# ============================================================================

@node
@mcp_tool("transaction_tracker")
def track_income(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use MCP tool to log income in database.
    """
    # Simulated MCP tool call
    transaction = {
        "type": "income",
        "amount": 5000.00,  # Would be extracted from user_query
        "category": "salary",
        "description": "Monthly salary",
        "date": datetime.now().isoformat(),
        "source": "Employer Inc."
    }
    
    return {
        **state,
        "response": {
            "type": "transaction_logged",
            "message": f"✅ Logged income: ${transaction['amount']} from {transaction['source']}",
            "transaction": transaction
        }
    }


# ============================================================================
# Node 2c: View Summary (MCP Tool + Analysis)
# ============================================================================

@node
@autonomous_agent(
    model="openai:gpt-4",
    tools=["transaction_query", "categorize_spending"],
    memory=True
)
def view_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Autonomous agent that:
    1. Queries MCP tool for transaction history
    2. Analyzes spending patterns
    3. Generates summary report
    """
    # Simulated data (in production, query from MCP tool)
    summary = {
        "total_income": 5000.00,
        "total_expenses": 3245.67,
        "savings": 1754.33,
        "savings_rate": 35.09,
        "top_categories": [
            {"category": "food", "amount": 890.50, "percentage": 27.4},
            {"category": "rent", "amount": 1500.00, "percentage": 46.2},
            {"category": "transport", "amount": 345.20, "percentage": 10.6},
            {"category": "entertainment", "amount": 509.97, "percentage": 15.7}
        ],
        "period": "This month"
    }
    
    message = f"""
📊 **Financial Summary**

**Income:** ${summary['total_income']:,.2f}
**Expenses:** ${summary['total_expenses']:,.2f}
**Savings:** ${summary['savings']:,.2f} ({summary['savings_rate']:.1f}%)

**Top Spending Categories:**
"""
    for cat in summary['top_categories']:
        message += f"\n• {cat['category'].title()}: ${cat['amount']:,.2f} ({cat['percentage']:.1f}%)"
    
    return {
        **state,
        "response": {
            "type": "summary",
            "message": message,
            "data": summary
        }
    }


# ============================================================================
# Node 2d: Budget Advice (Autonomous Agent)
# ============================================================================

@node
@autonomous_agent(
    model="openai:gpt-4",
    tools=["transaction_query", "budget_analyzer", "savings_calculator"],
    memory=True
)
def get_budget_advice(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Autonomous agent that:
    1. Analyzes spending patterns
    2. Compares to recommended budgets (50/30/20 rule)
    3. Suggests specific actions to save money
    """
    # Simulated analysis
    advice = {
        "current_allocation": {
            "needs": 65,  # Rent, utilities, groceries (should be 50%)
            "wants": 20,  # Entertainment, dining out (should be 30%)
            "savings": 15  # Investments, emergency fund (should be 20%)
        },
        "recommendations": [
            {
                "category": "food",
                "current": 890.50,
                "suggested": 650.00,
                "savings_potential": 240.50,
                "tips": [
                    "Meal prep on Sundays to reduce eating out",
                    "Use grocery list to avoid impulse buys",
                    "Shop at discount stores like Aldi or Costco"
                ]
            },
            {
                "category": "entertainment",
                "current": 509.97,
                "suggested": 300.00,
                "savings_potential": 209.97,
                "tips": [
                    "Share streaming subscriptions with family",
                    "Look for free local events",
                    "Use library for books and movies"
                ]
            }
        ],
        "total_savings_potential": 450.47
    }
    
    message = f"""
💡 **Budget Recommendations**

**Current Allocation:**
• Needs (rent, groceries): {advice['current_allocation']['needs']}% (target: 50%)
• Wants (entertainment): {advice['current_allocation']['wants']}% (target: 30%)
• Savings: {advice['current_allocation']['savings']}% (target: 20%)

**Action Items:**

**1. Food Spending** - Save ${advice['recommendations'][0]['savings_potential']:.2f}/month
"""
    for tip in advice['recommendations'][0]['tips']:
        message += f"\n   • {tip}"
    
    message += f"\n\n**2. Entertainment** - Save ${advice['recommendations'][1]['savings_potential']:.2f}/month"
    for tip in advice['recommendations'][1]['tips']:
        message += f"\n   • {tip}"
    
    message += f"\n\n💰 **Total Potential Savings: ${advice['total_savings_potential']:.2f}/month**"
    
    return {
        **state,
        "response": {
            "type": "budget_advice",
            "message": message,
            "data": advice
        }
    }


# ============================================================================
# Node 2e: Investment Advice (A2A Delegation)
# ============================================================================

@node
def delegate_to_investment_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delegate to specialized investment advisor agent via A2A protocol.
    
    In production, this would:
    1. Send request to remote investment agent
    2. Include user's financial profile (income, savings, risk tolerance)
    3. Receive personalized investment recommendations
    """
    # Simulated A2A call to investment advisor agent
    user_profile = {
        "age": 32,
        "monthly_savings": 1754.33,
        "emergency_fund": 15000.00,
        "risk_tolerance": "moderate",
        "investment_horizon": "long-term"
    }
    
    # In production: a2a_client.delegate("investment_advisor_agent", user_profile)
    
    investment_advice = {
        "recommended_allocation": {
            "stocks": 60,
            "bonds": 30,
            "cash": 10
        },
        "specific_recommendations": [
            {
                "type": "Index Fund",
                "ticker": "VTI",
                "allocation": 40,
                "reason": "Low-cost total market exposure"
            },
            {
                "type": "International Fund",
                "ticker": "VXUS",
                "allocation": 20,
                "reason": "Geographic diversification"
            },
            {
                "type": "Bond Fund",
                "ticker": "BND",
                "allocation": 30,
                "reason": "Stability and income"
            },
            {
                "type": "High-Yield Savings",
                "provider": "Marcus by Goldman Sachs",
                "allocation": 10,
                "reason": "Emergency fund with 4.5% APY"
            }
        ],
        "monthly_investment_plan": 1400.00,  # Leave some for short-term goals
        "projected_growth": {
            "5_years": 98500.00,
            "10_years": 235000.00,
            "20_years": 687000.00
        }
    }
    
    message = f"""
📈 **Investment Recommendations** (via Investment Advisor Agent)

**Recommended Asset Allocation:**
• Stocks: {investment_advice['recommended_allocation']['stocks']}%
• Bonds: {investment_advice['recommended_allocation']['bonds']}%
• Cash: {investment_advice['recommended_allocation']['cash']}%

**Specific Investments:**
"""
    for rec in investment_advice['specific_recommendations']:
        message += f"\n• **{rec['type']}** ({rec.get('ticker', rec.get('provider'))})"
        message += f"\n  - Allocate: {rec['allocation']}%"
        message += f"\n  - Why: {rec['reason']}"
    
    message += f"\n\n💸 **Monthly Investment: ${investment_advice['monthly_investment_plan']:.2f}**"
    message += f"\n\n**Projected Portfolio Value:**"
    message += f"\n• 5 years: ${investment_advice['projected_growth']['5_years']:,.2f}"
    message += f"\n• 10 years: ${investment_advice['projected_growth']['10_years']:,.2f}"
    message += f"\n• 20 years: ${investment_advice['projected_growth']['20_years']:,.2f}"
    
    return {
        **state,
        "response": {
            "type": "investment_advice",
            "message": message,
            "data": investment_advice,
            "delegated_to": "investment_advisor_agent"
        }
    }


# ============================================================================
# Workflow: Personal Finance Agent
# ============================================================================

@workflow_graph(
    start="parse_intent",
    routing={
        "parse_intent": lambda s: {
            "track_expense": "track_expense",
            "track_income": "track_income",
            "view_summary": "view_summary",
            "get_budget_advice": "get_budget_advice",
            "invest_advice": "delegate_to_investment_agent"
        }.get(s.get("intent"), "view_summary"),
        "track_expense": "END",
        "track_income": "END",
        "view_summary": "END",
        "get_budget_advice": "END",
        "delegate_to_investment_agent": "END"
    },
    end="END"
)
def personal_finance_agent(user_query: str) -> Dict[str, Any]:
    """
    Personal Financial Assistant workflow.
    
    Routes user queries to appropriate handlers:
    - Expense tracking → MCP tool
    - Income tracking → MCP tool
    - Summary → Autonomous agent with memory
    - Budget advice → Autonomous agent with analysis tools
    - Investment advice → A2A delegation to specialist agent
    """
    return {"user_query": user_query}


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("Personal Financial Assistant (AAF Demo)")
    print("="*70)
    print("\nDemonstrating MCP tools + A2A delegation + Workflow orchestration\n")
    
    # Example 1: Track expense
    print("\n" + "="*70)
    print("Example 1: Track Expense")
    print("="*70)
    result = personal_finance_agent("I spent $45.99 at Whole Foods")
    print(result["response"]["message"])
    
    # Example 2: View summary
    print("\n" + "="*70)
    print("Example 2: View Summary")
    print("="*70)
    result = personal_finance_agent("Show me my spending summary")
    print(result["response"]["message"])
    
    # Example 3: Get budget advice
    print("\n" + "="*70)
    print("Example 3: Budget Advice")
    print("="*70)
    result = personal_finance_agent("How can I save more money?")
    print(result["response"]["message"])
    
    # Example 4: Investment advice (A2A delegation)
    print("\n" + "="*70)
    print("Example 4: Investment Advice (A2A Delegation)")
    print("="*70)
    result = personal_finance_agent("What should I invest in?")
    print(result["response"]["message"])
    print(f"\n⚡ Delegated to: {result['response']['delegated_to']}")
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
This example demonstrates:

✅ **MCP Tool Integration**
   - track_expense() uses MCP transaction_tracker
   - track_income() uses MCP transaction_tracker
   - Simulates database operations

✅ **A2A Protocol**
   - delegate_to_investment_agent() calls remote specialist
   - Passes user financial profile
   - Receives expert recommendations

✅ **Autonomous Agents**
   - view_summary() uses agent with memory + tools
   - get_budget_advice() uses agent with analysis tools
   - Demonstrates multi-tool orchestration

✅ **Workflow Orchestration**
   - Conditional routing based on intent
   - Clean separation of concerns
   - Production-ready structure

🚀 **Next Steps:**
   1. Connect to real MCP server for database operations
   2. Deploy investment advisor as separate A2A agent
   3. Add authentication and user profiles
   4. Integrate with CopilotKit for beautiful UI
""")
