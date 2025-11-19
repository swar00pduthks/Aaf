"""
Example: Using AAF to orchestrate LangGraph agents

AAF serves as the middleware/orchestration layer while LangGraph
handles the stateful workflow logic.
"""

from aaf import (
    SequentialPattern,
    InMemoryShortTermMemory,
    ApprovalWorkflow
)
import logging

# Simulated LangGraph agent wrapper
class LangGraphAgentWrapper:
    """Wrapper for LangGraph agents to work with AAF protocols."""
    
    def __init__(self, agent_id: str, langgraph_agent, logger):
        self._agent_id = agent_id
        self._lg_agent = langgraph_agent  # Your actual LangGraph agent
        self._logger = logger
    
    @property
    def agent_id(self):
        return self._agent_id
    
    def initialize(self, config):
        """Initialize the LangGraph agent."""
        pass
    
    def execute(self, input_data):
        """
        Execute LangGraph agent and translate response to AAF format.
        
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
        self._logger.info(f"[{self._agent_id}] Executing LangGraph agent")
        
        # In real implementation:
        # result = self._lg_agent.invoke(input_data)
        
        # Simulated response
        return {
            "status": "success",
            "agent_id": self._agent_id,
            "result": f"LangGraph agent {self._agent_id} processed task",
            "framework": "LangGraph",
            "input": input_data
        }
    
    def shutdown(self):
        """Cleanup LangGraph resources."""
        pass


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
    
    # Wrap LangGraph agents with AAF protocol
    research_agent = LangGraphAgentWrapper("lg_researcher", None, logger)
    analysis_agent = LangGraphAgentWrapper("lg_analyst", None, logger)
    report_agent = LangGraphAgentWrapper("lg_reporter", None, logger)
    
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
