"""
Complete Example: Building an Agentic Research Assistant with AAF

This example demonstrates all major AAF components:
- Memory (short-term and long-term)
- Planning and reasoning (ReAct pattern)
- Multi-agent collaboration (sequential pattern)
- Human-in-the-loop (approval workflows)
- State management and retry logic
"""

import logging
from aaf import (
    InMemoryShortTermMemory,
    SimpleLongTermMemory,
    SimpleTaskPlanner,
    ReActReasoner,
    SequentialPattern,
    ApprovalWorkflow,
    ApprovalStatus,
    InMemoryStateManager,
    RetryPolicy,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleAgent:
    """Simple agent for demonstration purposes."""
    
    def __init__(self, agent_id: str, logger):
        self._agent_id = agent_id
        self._logger = logger
    
    @property
    def agent_id(self):
        return self._agent_id
    
    def initialize(self, config):
        pass
    
    def execute(self, input_data):
        self._logger.info(f"[{self._agent_id}] Executing task")
        return {
            "status": "success",
            "agent_id": self._agent_id,
            "result": f"Task completed by {self._agent_id}",
            "input": input_data
        }
    
    def shutdown(self):
        pass


def example_1_basic_agent_with_memory():
    """Example 1: Basic agent with short-term memory."""
    print("\n=== Example 1: Agent with Memory ===\n")
    
    memory = InMemoryShortTermMemory(logger=logger, max_entries=10)
    
    memory.add({
        "content": "User prefers concise responses",
        "metadata": {"type": "preference"}
    })
    
    memory.add({
        "content": "Previous conversation was about Python frameworks",
        "metadata": {"type": "context"}
    })
    
    recent_memories = memory.get_recent(count=5)
    print(f"Recent memories: {len(recent_memories)}")
    
    search_results = memory.search("Python", limit=5)
    print(f"Search for 'Python' found: {len(search_results)} results")
    
    return memory


def example_2_planning_and_reasoning():
    """Example 2: Task planning and ReAct reasoning."""
    print("\n=== Example 2: Planning and Reasoning ===\n")
    
    planner = SimpleTaskPlanner(logger=logger)
    reasoner = ReActReasoner(logger=logger)
    
    goal = "Search for weather data and analyze trends"
    available_services = ["mcp_tool_search", "mcp_tool_weather"]
    
    plan = planner.create_plan(
        goal=goal,
        context={"location": "San Francisco"},
        available_services=available_services
    )
    
    print(f"Created plan with {len(plan)} steps:")
    for step in plan:
        print(f"  - Step: {step['action']}: {step['description']}")
    
    reasoning = reasoner.reason(
        observation="Ready to start task",
        history=[],
        goal=goal
    )
    
    print(f"\nReasoning: {reasoning['thought']}")
    print(f"Action: {reasoning['action']['type']}")
    
    return planner, reasoner


def example_3_multi_agent_collaboration():
    """Example 3: Sequential multi-agent collaboration."""
    print("\n=== Example 3: Multi-Agent Collaboration ===\n")
    
    research_agent = SimpleAgent("researcher", logger)
    writer_agent = SimpleAgent("writer", logger)
    reviewer_agent = SimpleAgent("reviewer", logger)
    
    sequential = SequentialPattern(
        agents=[research_agent, writer_agent, reviewer_agent],
        logger=logger
    )
    
    initial_state = {
        "request": {
            "topic": "Agentic AI frameworks",
            "task": "research and summarize"
        }
    }
    
    result = sequential.execute(agents=[], initial_state=initial_state)
    
    print(f"Collaboration completed in {result['execution_time']:.2f}s")
    print(f"Execution chain: {len(result['execution_chain'])} steps")
    
    for step in result['execution_chain']:
        print(f"  - Step {step['step']}: {step['agent_id']} - {step['status']}")
    
    return result


def example_4_human_in_the_loop():
    """Example 4: Human approval workflow."""
    print("\n=== Example 4: Human-in-the-Loop ===\n")
    
    def custom_approval_handler(request):
        action = request["action"]
        print(f"\n[APPROVAL REQUIRED] {action}")
        print(f"Context: {request['context']}")
        return ApprovalStatus.APPROVED
    
    workflow = ApprovalWorkflow(
        approval_handler=custom_approval_handler,
        logger=logger
    )
    
    status = workflow.request_approval(
        action="Delete 100 user records",
        context={"reason": "Cleanup inactive accounts", "count": 100},
        timeout_seconds=60
    )
    
    print(f"\nApproval status: {status.value}")
    
    history = workflow.get_approval_history()
    print(f"Total approvals processed: {len(history)}")
    
    return workflow


def example_5_complete_agentic_system():
    """Example 5: Complete system with all components."""
    print("\n=== Example 5: Complete Agentic System ===\n")
    
    state_manager = InMemoryStateManager(logger=logger)
    memory = InMemoryShortTermMemory(logger=logger)
    planner = SimpleTaskPlanner(logger=logger)
    reasoner = ReActReasoner(logger=logger)
    approval_workflow = ApprovalWorkflow(logger=logger)
    
    goal = "Research AI agent frameworks and create a comparison report"
    
    memory.add({
        "content": "User needs a technical comparison of frameworks",
        "metadata": {"type": "requirement"}
    })
    
    plan = planner.create_plan(
        goal=goal,
        context={"format": "technical report"},
        available_services=["mcp_tool_search", "a2a_client_writer"]
    )
    
    print(f"Plan created with {len(plan)} steps")
    
    approval_status = approval_workflow.request_approval(
        action="Execute research plan",
        context={"goal": goal, "steps": len(plan)}
    )
    
    if approval_status == ApprovalStatus.APPROVED:
        print("Plan approved, starting execution...")
        
        for i, step in enumerate(plan):
            reasoning = reasoner.reason(
                observation=f"Executing step {i + 1}",
                history=[],
                goal=goal
            )
            
            print(f"\nStep {i + 1}: {step['action']}")
            print(f"Reasoning: {reasoning['thought']}")
            
            state_manager.save_state(
                agent_id="research_assistant",
                state={"current_step": i, "reasoning": reasoning}
            )
        
        print("\nExecution complete!")
        final_state = state_manager.load_state("research_assistant")
        print(f"Final state: {final_state}")
    else:
        print("Plan rejected by approval workflow")
    
    return {
        "state_manager": state_manager,
        "memory": memory,
        "planner": planner,
        "reasoner": reasoner,
        "approval_workflow": approval_workflow
    }


if __name__ == "__main__":
    print("=" * 60)
    print("AAF Complete Examples")
    print("=" * 60)
    
    example_1_basic_agent_with_memory()
    
    example_2_planning_and_reasoning()
    
    example_3_multi_agent_collaboration()
    
    example_4_human_in_the_loop()
    
    example_5_complete_agentic_system()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
