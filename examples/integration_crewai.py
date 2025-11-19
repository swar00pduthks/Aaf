"""
Example: Using AAF with CrewAI

AAF provides built-in CrewAIAdapter - just plug and play!

CrewAI provides:
- Role-based agent definition (role, goal, backstory)
- Crew and Flow orchestration
- Built-in delegation

AAF adds:
- Memory systems for context retention
- Planning abstractions
- Guardrails and safety validation
- REST API exposure
- Approval workflows
"""

from aaf import (
    InMemoryShortTermMemory,
    SimpleTaskPlanner,
    GuardrailValidator,
    ApprovalWorkflow,
    CrewAIAdapter  # Built-in adapter!
)
import logging


def run_crewai_integration():
    """
    Use Case: Content creation crew where CrewAI handles agent roles,
    but AAF provides memory, planning, and guardrails.
    """
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    # AAF Memory System
    memory = InMemoryShortTermMemory(logger=logger, max_entries=50)
    memory.add({
        "content": "User wants blog post about quantum computing",
        "metadata": {"type": "user_request", "format": "blog"}
    })
    
    # AAF Planning
    planner = SimpleTaskPlanner(logger=logger)
    plan = planner.create_plan(
        goal="Create technical blog post about quantum computing",
        context={"audience": "developers", "length": "1500 words"},
        available_services=["researcher", "writer", "editor"]
    )
    
    print(f"\nPlan created with {len(plan)} steps")
    for step in plan:
        print(f"  - {step['action']}: {step['description']}")
    
    # AAF Guardrails
    guardrail_rules = [
        {
            "name": "no_long_content",
            "condition": lambda action: action.get("word_count", 0) > 2000,
            "message": "Content exceeds 2000 words limit",
            "severity": "medium"
        },
        {
            "name": "requires_review",
            "condition": lambda action: action.get("topic") == "quantum computing",
            "message": "Technical topics require expert review",
            "severity": "high"
        }
    ]
    
    validator = GuardrailValidator(rules=guardrail_rules, logger=logger)
    
    # Validate action
    action = {
        "topic": "quantum computing",
        "word_count": 1500
    }
    
    is_safe = validator.validate(action)
    
    if not is_safe:
        violations = validator.get_violations()
        print(f"\nGuardrail violations detected:")
        for v in violations:
            print(f"  - {v['rule']}: {v['message']}")
        
        # Request human approval
        approval = ApprovalWorkflow(logger=logger)
        status = approval.request_approval(
            action="Proceed with quantum computing content",
            context={"violations": [v['rule'] for v in violations]}
        )
        
        if status.value != "approved":
            print("Content creation blocked by guardrails")
            return
    
    # Wrap CrewAI agents with AAF's built-in adapter
    # In real code, replace None with your actual CrewAI agents:
    # from crewai import Agent
    # crew_agent = Agent(role="Researcher", goal="...", backstory="...")
    
    researcher = CrewAIAdapter("crew_researcher", None, logger)
    writer = CrewAIAdapter("crew_writer", None, logger)
    
    # Execute (simplified)
    print(f"\nExecuting CrewAI agents with AAF orchestration...")
    research_result = researcher.execute({"query": "quantum computing basics"})
    write_result = writer.execute({"draft_from": research_result})
    
    # Store in memory
    memory.add({
        "content": "Blog post completed successfully",
        "metadata": {"steps": 2, "framework": "CrewAI + AAF"}
    })
    
    print(f"\nIntegration complete!")
    return {"research": research_result, "content": write_result}


if __name__ == "__main__":
    result = run_crewai_integration()
    print(f"\nFinal result: {result}")
