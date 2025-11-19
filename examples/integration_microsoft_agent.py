"""
Example: Using AAF with Microsoft Agent Framework

AAF provides built-in MicrosoftAgentAdapter - no wrapper code needed!

Microsoft Agent Framework provides:
- Multi-agent patterns (sequential, concurrent, handoff, group chat)
- MCP (Model Context Protocol) support
- A2A (Agent-to-Agent) communication

AAF adds:
- REST API exposure
- Centralized memory management
- Human-in-the-loop workflows
- Retry policies with exponential backoff
- State persistence across sessions
"""

from aaf import (
    HierarchicalPattern,
    InMemoryStateManager,
    RetryPolicy,
    MicrosoftAgentAdapter  # Built-in adapter!
)
import logging


def run_microsoft_agent_integration():
    """
    Use Case: Hierarchical agent system where manager and workers
    are Microsoft agents, but AAF provides the production infrastructure.
    """
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    # Create state manager for persistence
    state_mgr = InMemoryStateManager(logger=logger)
    
    # Wrap Microsoft agents with AAF's built-in adapter
    # In real code, replace None with your actual Microsoft agents:
    # from agent_framework import ChatAgent
    # ms_agent = ChatAgent(...)
    
    manager = MicrosoftAgentAdapter("ms_manager", None, logger)
    worker1 = MicrosoftAgentAdapter("ms_researcher", None, logger)
    worker2 = MicrosoftAgentAdapter("ms_analyst", None, logger)
    worker3 = MicrosoftAgentAdapter("ms_writer", None, logger)
    
    # Use AAF's hierarchical pattern
    hierarchy = HierarchicalPattern(
        manager_agent=manager,
        worker_agents=[worker1, worker2, worker3],
        logger=logger
    )
    
    # Add retry policy (AAF feature)
    retry_policy = RetryPolicy(
        max_retries=3,
        initial_delay=1.0,
        exponential_base=2.0,
        jitter=True
    )
    
    # Execute with retry protection
    result = hierarchy.execute(
        agents=[],
        initial_state={
            "request": {
                "task": "Analyze market trends and create report",
                "deadline": "2 hours"
            }
        }
    )
    
    # Persist state (AAF feature)
    state_mgr.save_state(
        agent_id="market_analysis_team",
        state={
            "result": result,
            "manager": manager.agent_id,
            "workers": [w.agent_id for w in [worker1, worker2, worker3]]
        }
    )
    
    print(f"\nHierarchical execution completed")
    print(f"Worker results: {len(result.get('worker_results', []))}")
    
    return result


if __name__ == "__main__":
    result = run_microsoft_agent_integration()
    print(f"\nFinal result: {result}")
