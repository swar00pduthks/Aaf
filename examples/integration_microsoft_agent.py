"""
Example: Using AAF with Microsoft Agent Framework

AAF provides the REST API layer and production features while
Microsoft Agent Framework handles agent execution.
"""

from aaf import (
    HierarchicalPattern,
    InMemoryStateManager,
    RetryPolicy,
    RetryMiddleware
)
import logging


class MicrosoftAgentWrapper:
    """
    Wrapper for Microsoft Agent Framework agents.
    
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
    
    def __init__(self, agent_id: str, ms_agent, logger):
        self._agent_id = agent_id
        self._ms_agent = ms_agent  # Your Microsoft Agent Framework agent
        self._logger = logger
    
    @property
    def agent_id(self):
        return self._agent_id
    
    def initialize(self, config):
        pass
    
    def execute(self, input_data):
        self._logger.info(f"[{self._agent_id}] Executing Microsoft Agent")
        
        # In real implementation:
        # result = await self._ms_agent.run_async(input_data["query"])
        
        return {
            "status": "success",
            "agent_id": self._agent_id,
            "result": f"Microsoft Agent {self._agent_id} completed",
            "framework": "Microsoft Agent Framework",
            "input": input_data
        }
    
    def shutdown(self):
        pass


def run_microsoft_agent_integration():
    """
    Use Case: Hierarchical agent system where manager and workers
    are Microsoft agents, but AAF provides the production infrastructure.
    """
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    # Create state manager for persistence
    state_mgr = InMemoryStateManager(logger=logger)
    
    # Wrap Microsoft agents
    manager = MicrosoftAgentWrapper("ms_manager", None, logger)
    worker1 = MicrosoftAgentWrapper("ms_researcher", None, logger)
    worker2 = MicrosoftAgentWrapper("ms_analyst", None, logger)
    worker3 = MicrosoftAgentWrapper("ms_writer", None, logger)
    
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
