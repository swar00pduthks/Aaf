"""
Real-World Chat Client Workflow Example

This demonstrates AAF's node-based workflow orchestration with:
- Nodes (steps in workflow)
- Conditional routing (if-then-else logic)
- State management (passing data between nodes)
- LLM calls (@llm)
- MCP tool integration (@mcp_tool)
- Autonomous agents (@autonomous_agent)

Use Case: Chat client where:
1. User posts a query
2. LLM determines if it's a SQL query or MCP tool request
3. Route to SQL generation OR tool call
4. Format final response
"""

from aaf import node, workflow_graph, llm, mcp_tool, autonomous_agent
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


# =============================================================================
# Define Workflow Nodes
# =============================================================================

# Node 1: Parse user intent using LLM
@node
@llm(model="openai:gpt-4")
def parse_intent(state):
    """
    Determine if user query is asking for:
    - Database query (SQL)
    - Tool request (search, weather, etc.)
    - Research task (needs autonomous agent)
    """
    query = state["user_query"]
    
    # LLM analyzes the query
    # In real implementation, LLM would return structured output
    # For demo, we simulate intent detection
    
    if "user" in query.lower() or "database" in query.lower():
        intent = "database"
    elif "research" in query.lower():
        intent = "research"
    else:
        intent = "tool"
    
    print(f"📋 Intent detected: {intent}")
    return {"intent": intent, "original_query": query}


# Node 2a: Generate SQL using LLM (for database queries)
@node
@llm(model="openai:gpt-4")
def generate_sql(state):
    """Convert natural language to SQL query."""
    query = state["user_query"]
    
    # LLM generates SQL
    # In real implementation, LLM would generate actual SQL
    sql = f"SELECT * FROM users WHERE name LIKE '%{query}%'"
    
    print(f"💾 Generated SQL: {sql}")
    return {"sql": sql, "query_type": "database"}


# Node 2b: Call MCP tool (for tool requests)
@node
@mcp_tool("search")
def call_search_tool(state):
    """Call MCP search tool."""
    query = state["user_query"]
    
    # MCP tool executes search
    mcp_result = state.get("_mcp_result", {})
    
    print(f"🔍 Search completed: {mcp_result.get('status')}")
    return {
        "search_results": mcp_result.get("result"),
        "query_type": "tool"
    }


# Node 2c: Autonomous research agent (for complex research)
@node
@autonomous_agent(
    model="openai:gpt-4",
    tools=["search", "weather", "calculator"],
    memory=True,
    planning=True
)
def research_agent(state):
    """
    Autonomous agent that can:
    - Plan multi-step approach
    - Use multiple tools
    - Remember context
    - Make autonomous decisions
    """
    query = state["user_query"]
    
    # Agent handles everything autonomously
    tool_history = state.get("_tool_history", [])
    
    print(f"🤖 Research agent used {len(tool_history)} tools")
    return {
        "research_results": "Comprehensive research findings...",
        "query_type": "research",
        "tools_used": [t["tool"] for t in tool_history]
    }


# Node 3: Format final response
@node
def format_response(state):
    """Format the final response based on query type."""
    query_type = state.get("query_type")
    
    if query_type == "database":
        response = {
            "type": "sql",
            "query": state.get("sql"),
            "message": "Here's your SQL query"
        }
    elif query_type == "tool":
        response = {
            "type": "search",
            "results": state.get("search_results"),
            "message": "Here are your search results"
        }
    elif query_type == "research":
        response = {
            "type": "research",
            "findings": state.get("research_results"),
            "tools_used": state.get("tools_used", []),
            "message": "Here's your research"
        }
    else:
        response = {"error": "Unknown query type"}
    
    print(f"✅ Response formatted: {response['type']}")
    return {"response": response}


# =============================================================================
# Build Workflow Graph with Conditional Routing
# =============================================================================

@workflow_graph(
    start="parse_intent",
    routing={
        # After parsing intent, route based on intent type
        "parse_intent": lambda state: {
            "database": "generate_sql",
            "tool": "call_search_tool",
            "research": "research_agent"
        }[state["intent"]],
        
        # All paths lead to format_response
        "generate_sql": "format_response",
        "call_search_tool": "format_response",
        "research_agent": "format_response",
        
        # End after formatting
        "format_response": "END"
    },
    end="END"
)
def chat_workflow(user_query: str):
    """
    Complete chat client workflow with conditional routing.
    
    Flow:
    1. parse_intent → determines intent
    2. Route to: generate_sql OR call_search_tool OR research_agent
    3. format_response → final output
    """
    return {"user_query": user_query}


# =============================================================================
# Run Examples
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("AAF Chat Client Workflow - Node-Based Orchestration")
    print("="*70)
    
    # Example 1: Database query
    print("\n" + "="*70)
    print("Example 1: Database Query")
    print("="*70)
    result1 = chat_workflow("Show me all users in the database")
    print(f"\n📤 Final Response:")
    print(f"   Type: {result1['response']['type']}")
    print(f"   Query: {result1['response'].get('query')}")
    print(f"   Message: {result1['response']['message']}")
    
    # Example 2: Tool request
    print("\n" + "="*70)
    print("Example 2: Tool Request")
    print("="*70)
    result2 = chat_workflow("Search for latest AI news")
    print(f"\n📤 Final Response:")
    print(f"   Type: {result2['response']['type']}")
    print(f"   Message: {result2['response']['message']}")
    
    # Example 3: Research task
    print("\n" + "="*70)
    print("Example 3: Research Task (Autonomous Agent)")
    print("="*70)
    result3 = chat_workflow("Research quantum computing applications")
    print(f"\n📤 Final Response:")
    print(f"   Type: {result3['response']['type']}")
    print(f"   Tools Used: {result3['response'].get('tools_used', [])}")
    print(f"   Message: {result3['response']['message']}")
    
    # Show workflow graph
    print("\n" + "="*70)
    print("Workflow Graph Structure")
    print("="*70)
    print("\nNodes:")
    for node_id, node in chat_workflow.graph.nodes.items():
        print(f"  • {node_id}: {node.description[:50]}...")
    
    print("\nRouting:")
    print("  parse_intent → (conditional)")
    print("    ├─ database → generate_sql")
    print("    ├─ tool → call_search_tool")
    print("    └─ research → research_agent")
    print("  All → format_response → END")
    
    print("\n" + "="*70)
    print("Key Concepts Demonstrated")
    print("="*70)
    print("""
1. Nodes (@node)
   - Steps in workflow graph
   - Process state and return updated state
   
2. LLM Calls (@llm)
   - Simple one-shot LLM calls
   - Used for intent detection, SQL generation
   
3. MCP Tools (@mcp_tool)
   - External tool integration
   - Call search, weather, database tools
   
4. Autonomous Agents (@autonomous_agent)
   - Real agents with tools, memory, planning
   - Can make autonomous decisions
   
5. Conditional Routing
   - Route based on state values
   - if-then-else logic in workflows
   
6. State Management
   - Pass data between nodes
   - Each node adds to state
""")
    
    print("="*70)
