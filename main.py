"""
Agentic Application Framework (AAF) - Main Demo

Demonstrates AAF's decorator-based approach for building agentic workflows.
Run this to see AAF in action!
"""

from examples.chat_client_workflow import chat_workflow


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 Agentic Application Framework (AAF) - Demo")
    print("="*70)
    print("\nAAF provides simple decorators for building agentic applications:")
    print("  • @node - workflow steps")
    print("  • @workflow_graph - orchestrate nodes with conditional routing")
    print("  • @llm - simple LLM calls")
    print("  • @autonomous_agent - real agents with tools, memory, planning")
    print("  • @mcp_tool - MCP tool integration")
    print("  • @a2a - agent-to-agent communication")
    
    print("\n" + "="*70)
    print("Running Chat Client Workflow Example...")
    print("="*70)
    
    # Example 1: Database query
    print("\n📊 Example 1: Database Query")
    print("-" * 70)
    result = chat_workflow("Show me all users in the database")
    print(f"✅ Result: {result['response']['type']}")
    print(f"   SQL: {result['response'].get('query', 'N/A')}")
    
    # Example 2: Tool request
    print("\n🔍 Example 2: Tool Request")
    print("-" * 70)
    result = chat_workflow("Search for latest AI news")
    print(f"✅ Result: {result['response']['type']}")
    print(f"   Message: {result['response']['message']}")
    
    # Example 3: Autonomous agent
    print("\n🤖 Example 3: Autonomous Agent")
    print("-" * 70)
    result = chat_workflow("Research quantum computing applications")
    print(f"✅ Result: {result['response']['type']}")
    print(f"   Tools Used: {result['response'].get('tools_used', [])}")
    print(f"   Message: {result['response']['message']}")
    
    print("\n" + "="*70)
    print("✨ Demo Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Check examples/chat_client_workflow.py for full code")
    print("  2. Run FastAPI server: python api.py")
    print("  3. Visit http://localhost:5000/docs for API documentation")
    print("  4. Build your own workflows with @node and @workflow_graph")
    print("\n" + "="*70 + "\n")
