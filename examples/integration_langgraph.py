"""
Example: Using AAF to orchestrate LangGraph agents

AAF provides built-in adapters for popular frameworks. No need to write
wrapper classes - just use LangGraphAdapter!

AAF provides:
- Memory management
- Human-in-the-loop workflows  
- Retry logic
- State persistence

LangGraph provides:
- Stateful graph execution
- Conditional branching
- Checkpointing
"""

from aaf import (
    SequentialPattern,
    InMemoryShortTermMemory,
    ApprovalWorkflow,
    LangGraphAdapter  # Built-in adapter!
)
import logging


# Example: Multi-agent workflow with LangGraph agents orchestrated by AAF
def run_langgraph_integration():
    """
    Use Case: Research pipeline where each agent is a LangGraph workflow,
    but AAF handles memory, approvals, and cross-agent coordination.
    """
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    # Create memory system (AAF feature)
    memory = InMemoryShortTermMemory(logger=logger)
    memory.add({
        "content": "User wants technical comparison of AI frameworks",
        "metadata": {"type": "requirement"}
    })
    
    # Wrap LangGraph agents with AAF's built-in adapter
    # In real code, replace None with your actual LangGraph agents:
    # from langgraph.prebuilt import create_react_agent
    # lg_agent = create_react_agent(model, tools)
    
    research_agent = LangGraphAdapter("lg_researcher", None, logger)
    analysis_agent = LangGraphAdapter("lg_analyst", None, logger)
    report_agent = LangGraphAdapter("lg_reporter", None, logger)
    
    # Use AAF's sequential pattern for orchestration
    pipeline = SequentialPattern(
        agents=[research_agent, analysis_agent, report_agent],
        logger=logger
    )
    
    # Add human-in-the-loop (AAF feature)
    approval = ApprovalWorkflow(logger=logger)
    status = approval.request_approval(
        action="Execute research pipeline with LangGraph agents",
        context={"num_agents": 3, "framework": "LangGraph"}
    )
    
    if status.value == "approved":
        # Execute pipeline
        result = pipeline.execute(
            agents=[],
            initial_state={
                "request": {
                    "topic": "AI frameworks comparison",
                    "depth": "technical"
                }
            }
        )
        
        # Store in memory
        memory.add({
            "content": f"Pipeline completed: {result['status']}",
            "metadata": {"execution_time": result.get("execution_time", 0)}
        })
        
        print(f"\nPipeline completed in {result.get('execution_time', 0):.2f}s")
        print(f"Execution chain: {len(result['execution_chain'])} steps")
    
    return result


if __name__ == "__main__":
    result = run_langgraph_integration()
    print(f"\nFinal result: {result}")
