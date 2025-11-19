"""
Databricks Integration Examples for AAF

Shows how to integrate:
1. Databricks Gemini (LLM Provider)
2. Databricks Genie (Text-to-SQL Agent)
"""

import sys
sys.path.insert(0, '/home/runner/workspace')
import os
from aaf import node, workflow_graph


# ============================================================================
# Example 1: Use Databricks Gemini as LLM Provider
# ============================================================================

def demo_gemini_as_llm():
    """
    Use Google's Gemini models hosted on Databricks as an LLM provider.
    
    Alternative to OpenAI, Anthropic, etc.
    """
    print("\n" + "="*70)
    print("Example 1: Databricks Gemini as LLM Provider")
    print("="*70)
    
    from aaf.databricks_integration import DatabricksGeminiProvider
    
    print("\n✅ Databricks Gemini Provider")
    print("\nAvailable Models:")
    print("  • gemini-2.5-pro   - Advanced reasoning, 1M token context")
    print("  • gemini-2.5-flash - Fast, cost-efficient")
    print("  • gemini-3-pro     - Latest frontier model")
    
    print("\nSetup:")
    print("""
    from aaf.databricks_integration import DatabricksGeminiProvider
    
    # Create provider
    provider = DatabricksGeminiProvider(
        workspace_url="https://myworkspace.databricks.com",
        token=os.environ["DATABRICKS_TOKEN"],
        model="gemini-2.5-flash"
    )
    
    # Use with @llm decorator
    from aaf import llm
    
    @llm(provider=provider, model="gemini-2.5-flash")
    def analyze_sentiment(state):
        return {"sentiment": "positive"}
    """)
    
    print("\n📌 Benefits:")
    print("  • Pay through Databricks contract")
    print("  • Data stays in Databricks security perimeter")
    print("  • OpenAI-compatible API")
    print("  • Can use SQL ai_query() for batch processing")


# ============================================================================
# Example 2: Use Databricks Genie for Text-to-SQL
# ============================================================================

def demo_genie_agent():
    """
    Use Databricks Genie as a text-to-SQL agent.
    
    Genie converts natural language to SQL and executes queries.
    """
    print("\n" + "="*70)
    print("Example 2: Databricks Genie as SQL Agent")
    print("="*70)
    
    from aaf.databricks_integration import DatabricksGenieAgent
    
    print("\n✅ Databricks Genie Agent")
    print("\nWhat is Genie?")
    print("  • Converts natural language → SQL")
    print("  • Executes queries against Unity Catalog")
    print("  • Returns results + natural language summary")
    print("  • Supports follow-up questions")
    
    print("\nSetup:")
    print("""
    from aaf.databricks_integration import DatabricksGenieAgent
    
    # Create Genie agent
    genie = DatabricksGenieAgent(
        workspace_url="https://myworkspace.databricks.com",
        space_id="abc123",  # From Genie space URL
        token=os.environ["DATABRICKS_TOKEN"]
    )
    
    # Ask questions
    result = genie.ask("What are total sales by region this quarter?")
    
    print(f"SQL: {result['sql']}")
    print(f"Results: {result['result']}")
    print(f"Summary: {result['summary']}")
    """)
    
    print("\n📌 What Genie Returns:")
    print("  • sql: Generated SQL query")
    print("  • result: Query results (table)")
    print("  • summary: Natural language explanation")
    print("  • thinking_steps: Chain-of-thought reasoning")
    print("  • conversation_id: For follow-up questions")


# ============================================================================
# Example 3: Integrate Genie into AAF Workflow
# ============================================================================

def demo_genie_in_workflow():
    """
    Show how to use Genie as a node in an AAF workflow.
    """
    print("\n" + "="*70)
    print("Example 3: Genie in AAF Workflow")
    print("="*70)
    
    print("\n✅ Use Genie as a workflow node:")
    print("""
    from aaf import node, workflow_graph
    from aaf.databricks_integration import DatabricksGenieAgent
    
    # Initialize Genie
    genie = DatabricksGenieAgent(
        workspace_url="https://myworkspace.databricks.com",
        space_id="sales_analytics"
    )
    
    # Parse user intent
    @node
    def parse_intent(state):
        query = state["user_query"].lower()
        
        if "sales" in query or "revenue" in query:
            return {"intent": "genie", "original_query": state["user_query"]}
        else:
            return {"intent": "other", "original_query": state["user_query"]}
    
    # Use Genie for data questions
    @node
    def ask_genie(state):
        result = genie.ask(state["original_query"])
        
        return {
            "type": "sql",
            "sql": result["sql"],
            "data": result["result"],
            "explanation": result["summary"]
        }
    
    # Format response
    @node
    def format_response(state):
        return {
            "response": {
                "type": state["type"],
                "sql": state.get("sql"),
                "explanation": state.get("explanation"),
                "message": "Here's your data analysis"
            }
        }
    
    # Orchestrate workflow
    @workflow_graph(
        start="parse_intent",
        routing={
            "parse_intent": lambda s: "ask_genie" if s["intent"] == "genie" else "format_response",
            "ask_genie": "format_response",
            "format_response": "END"
        }
    )
    def data_assistant(user_query: str):
        return {"user_query": user_query}
    
    # Use it
    result = data_assistant("What are our top products by revenue?")
    print(result["response"]["explanation"])
    """)


# ============================================================================
# Example 4: Multi-Agent System with Genie
# ============================================================================

def demo_multi_agent_with_genie():
    """
    Show multi-agent system where Genie handles SQL queries.
    """
    print("\n" + "="*70)
    print("Example 4: Multi-Agent System with Genie")
    print("="*70)
    
    print("\n✅ Route different query types to different agents:")
    print("""
    from aaf import node, workflow_graph, autonomous_agent
    from aaf.databricks_integration import DatabricksGenieAgent
    
    # Initialize specialized agents
    genie_sales = DatabricksGenieAgent(
        workspace_url="https://myworkspace.databricks.com",
        space_id="sales_space"
    )
    
    genie_finance = DatabricksGenieAgent(
        workspace_url="https://myworkspace.databricks.com",
        space_id="finance_space"
    )
    
    @node
    def route_query(state):
        query = state["user_query"].lower()
        
        if "sales" in query or "customer" in query:
            return {"target": "sales"}
        elif "cost" in query or "budget" in query:
            return {"target": "finance"}
        else:
            return {"target": "general"}
    
    @node
    def sales_agent(state):
        result = genie_sales.ask(state["user_query"])
        return {"response": result}
    
    @node
    def finance_agent(state):
        result = genie_finance.ask(state["user_query"])
        return {"response": result}
    
    @workflow_graph(
        start="route_query",
        routing={
            "route_query": lambda s: {
                "sales": "sales_agent",
                "finance": "finance_agent",
                "general": "END"
            }[s["target"]],
            "sales_agent": "END",
            "finance_agent": "END"
        }
    )
    def intelligent_assistant(user_query: str):
        return {"user_query": user_query}
    """)
    
    print("\n📌 Benefits:")
    print("  • Each Genie space is specialized (sales, finance, logistics)")
    print("  • Domain-specific data and business rules")
    print("  • Better accuracy than generic SQL generation")
    print("  • Unity Catalog permissions enforced")


# ============================================================================
# Example 5: Setup Instructions
# ============================================================================

def demo_setup_instructions():
    """
    Show how to set up Databricks integration.
    """
    print("\n" + "="*70)
    print("Setup Instructions")
    print("="*70)
    
    print("\n📋 Step 1: Get Databricks Credentials")
    print("""
    1. Go to your Databricks workspace
    2. User Settings → Access Tokens
    3. Generate new token
    4. Save as DATABRICKS_TOKEN environment variable
    """)
    
    print("\n📋 Step 2: Get Workspace URL")
    print("""
    Your workspace URL looks like:
      https://<workspace-id>.databricks.com
    
    Example:
      https://adb-123456789.azuredatabricks.net
    """)
    
    print("\n📋 Step 3: Get Genie Space ID (for Genie)")
    print("""
    1. Navigate to Genie space in Databricks UI
    2. Copy space ID from URL:
       https://<workspace>/sql/genie/rooms/<space-id>
    """)
    
    print("\n📋 Step 4: Install Dependencies")
    print("""
    pip install openai requests
    """)
    
    print("\n📋 Step 5: Use in AAF")
    print("""
    import os
    from aaf.databricks_integration import (
        DatabricksGeminiProvider,
        DatabricksGenieAgent
    )
    
    # For Gemini LLM
    gemini = DatabricksGeminiProvider(
        workspace_url=os.environ["DATABRICKS_WORKSPACE_URL"],
        token=os.environ["DATABRICKS_TOKEN"],
        model="gemini-2.5-flash"
    )
    
    # For Genie SQL agent
    genie = DatabricksGenieAgent(
        workspace_url=os.environ["DATABRICKS_WORKSPACE_URL"],
        space_id=os.environ["DATABRICKS_GENIE_SPACE_ID"],
        token=os.environ["DATABRICKS_TOKEN"]
    )
    """)


# ============================================================================
# Main Demo
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Databricks Integration with AAF")
    print("="*70)
    print("\nAAF supports two Databricks integrations:")
    print("  1. Databricks Gemini - Google's Gemini models as LLM provider")
    print("  2. Databricks Genie  - Text-to-SQL conversational agent")
    
    demo_gemini_as_llm()
    demo_genie_agent()
    demo_genie_in_workflow()
    demo_multi_agent_with_genie()
    demo_setup_instructions()
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
Databricks Integration Options:

1. **Databricks Gemini** (LLM Provider)
   • Type: API (OpenAI-compatible)
   • Use: Alternative to OpenAI/Anthropic
   • Models: Gemini 2.5 Pro, Flash, Gemini 3 Pro
   • AAF Integration: @llm decorator with custom provider

2. **Databricks Genie** (SQL Agent)
   • Type: Conversational agent with API
   • Use: Natural language → SQL queries
   • Features: Chain-of-thought reasoning, Unity Catalog
   • AAF Integration: @node or @autonomous_agent wrapper

Key Benefits:
  ✅ Data stays in Databricks security perimeter
  ✅ Pay through Databricks contract
  ✅ Unified governance via Unity Catalog
  ✅ Easy AAF integration

Next Steps:
  1. Set DATABRICKS_TOKEN environment variable
  2. Choose Gemini (LLM) or Genie (SQL) or both
  3. See examples above for integration code
  4. Deploy with AAF workflow orchestration
""")
    print("="*70 + "\n")
