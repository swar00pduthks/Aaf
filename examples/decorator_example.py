"""
AAF's Standout Feature: Zero-Boilerplate Decorators

Lambda-like simplicity for creating agents from any framework.
This is what makes AAF unique - not recreating Pydantic AI!
"""

from aaf.decorators import (
    agent,
    langgraph_agent,
    crewai_agent,
    microsoft_agent,
    workflow,
    list_agents
)
from aaf import SequentialPattern


# =============================================================================
# Example 1: Simple Function → Agent (Zero Boilerplate!)
# =============================================================================

@agent
def researcher(query: str) -> str:
    """Just decorate your function - it's now an AAF agent!"""
    print(f"🔍 Researching: {query}")
    return f"Research findings for: {query}"


@agent
def analyzer(data) -> str:
    """Another agent - still zero boilerplate!"""
    data_str = str(data) if not isinstance(data, str) else data
    print(f"📊 Analyzing: {data_str[:30]}...")
    return f"Analysis complete: {len(data_str)} chars processed"


@agent(agent_id="custom_writer")
def writer(analysis: str) -> str:
    """Custom agent ID for clarity."""
    print(f"✍️ Writing report...")
    return f"Report: {analysis}"


# =============================================================================
# Example 2: Framework-Specific Decorators
# =============================================================================

@langgraph_agent
def my_langgraph_agent(messages):
    """Wrap your LangGraph agent - one line!"""
    # In real code: return langgraph_instance.invoke(messages)
    print("🔗 LangGraph agent executing...")
    return {"result": "LangGraph processed"}


@crewai_agent
def my_crewai_agent(task):
    """Wrap your CrewAI agent - one line!"""
    # In real code: return crew.kickoff()
    print("👥 CrewAI agent executing...")
    return {"result": "CrewAI completed"}


@microsoft_agent
def my_microsoft_agent(query):
    """Wrap your Microsoft agent - one line!"""
    # In real code: return ms_agent.run_async(query)
    print("🏢 Microsoft agent executing...")
    return {"result": "Microsoft agent done"}


# =============================================================================
# Example 3: Workflow Decorator (Auto-Orchestration!)
# =============================================================================

@workflow(researcher, analyzer, writer, pattern="sequential")
def research_pipeline(query: str):
    """
    This decorator automatically orchestrates the 3 agents!
    No manual SequentialPattern setup needed!
    """
    pass  # The decorator handles everything!


# =============================================================================
# Example 4: Manual Orchestration (If You Need Control)
# =============================================================================

def manual_orchestration_example():
    """You can still orchestrate manually if needed."""
    
    # All decorated agents are AAF-compatible
    pipeline = SequentialPattern(agents=[
        researcher,
        analyzer,
        writer
    ])
    
    result = pipeline.execute(
        agents=[],
        initial_state={"request": {"query": "AI trends 2025"}}
    )
    
    return result


# =============================================================================
# Example 5: Mix Everything!
# =============================================================================

@workflow(
    researcher,           # Simple function
    my_langgraph_agent,  # LangGraph
    my_crewai_agent,     # CrewAI
    my_microsoft_agent,  # Microsoft
    writer,              # Another function
    pattern="sequential"
)
def multi_framework_pipeline(query: str):
    """
    Orchestrate agents from ANY framework with ONE decorator!
    This is AAF's killer feature!
    """
    pass


# =============================================================================
# Run Examples
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("AAF Decorator Examples - Zero Boilerplate!")
    print("="*60)
    
    # Example 1: Call agents directly
    print("\n1️⃣ Call decorated agents directly:")
    print(researcher("quantum computing"))
    
    # Example 2: Use as AAF agents
    print("\n2️⃣ Use as AAF agents:")
    result = researcher.execute({"query": "machine learning"})
    print(f"Result: {result}")
    
    # Example 3: List all registered agents
    print("\n3️⃣ List all registered agents:")
    print(f"Agents: {list_agents()}")
    
    # Example 4: Manual orchestration
    print("\n4️⃣ Manual orchestration:")
    result = manual_orchestration_example()
    print(f"Pipeline status: {result['status']}")
    print(f"Execution chain: {len(result['execution_chain'])} agents")
    
    # Example 5: Workflow decorator
    print("\n5️⃣ Workflow decorator (auto-orchestration):")
    result = research_pipeline("AI agents 2025")
    print(f"Workflow status: {result['status']}")
    
    # Example 6: Multi-framework pipeline
    print("\n6️⃣ Multi-framework pipeline:")
    result = multi_framework_pipeline("Future of AI")
    print(f"Multi-framework status: {result['status']}")
    
    print("\n" + "="*60)
    print("✨ AAF's Standout: Zero-Boilerplate Agent Creation!")
    print("="*60)
