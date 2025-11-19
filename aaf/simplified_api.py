"""
Simplified API facade for AAF - hides protocol complexity from end users.

This module provides a high-level, developer-friendly API that abstracts
away the protocol-oriented architecture. Perfect for users who want to
get started quickly without understanding the underlying abstractions.
"""

from typing import Dict, Any, List, Optional, Callable
import logging
from aaf import (
    InMemoryShortTermMemory,
    SimpleTaskPlanner,
    ReActReasoner,
    SequentialPattern,
    HierarchicalPattern,
    SwarmPattern,
    ApprovalWorkflow,
    GuardrailValidator,
    InMemoryStateManager,
    AgentRegistry
)


class Agent:
    """
    Simplified agent class that hides protocol complexity.
    
    Example:
        >>> agent = Agent("my_agent")
        >>> result = agent.run({"task": "analyze data"})
    """
    
    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(__name__)
    
    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return the result."""
        self._logger.info(f"[{self.name}] Running task")
        return {
            "status": "success",
            "agent": self.name,
            "result": f"Task completed by {self.name}",
            "input": task
        }


class Memory:
    """
    Simplified memory interface.
    
    Example:
        >>> memory = Memory()
        >>> memory.remember("User prefers technical details")
        >>> results = memory.recall("technical")
    """
    
    def __init__(self, max_size: int = 100):
        self._memory = InMemoryShortTermMemory(
            max_entries=max_size,
            ttl_seconds=3600
        )
    
    def remember(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Store a memory."""
        self._memory.add({
            "content": content,
            "metadata": metadata or {}
        })
    
    def recall(self, query: str, limit: int = 10) -> List[str]:
        """Search memories and return content only."""
        results = self._memory.search(query, limit=limit)
        return [r.get("content", "") for r in results]
    
    def recent(self, count: int = 5) -> List[str]:
        """Get recent memories."""
        results = self._memory.get_recent(count=count)
        return [r.get("content", "") for r in results]


class Planner:
    """
    Simplified planning interface.
    
    Example:
        >>> planner = Planner()
        >>> steps = planner.plan("Research AI and write report")
    """
    
    def __init__(self):
        self._planner = SimpleTaskPlanner()
    
    def plan(
        self,
        goal: str,
        available_tools: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """Create a plan for achieving a goal."""
        plan = self._planner.create_plan(
            goal=goal,
            context={},
            available_services=available_tools or []
        )
        
        # Simplify output
        return [
            {"action": step["action"], "description": step["description"]}
            for step in plan
        ]


class Team:
    """
    Simplified multi-agent team interface.
    
    Example:
        >>> team = Team([agent1, agent2, agent3], pattern="sequential")
        >>> result = team.execute({"task": "create report"})
    """
    
    def __init__(
        self,
        agents: List[Agent],
        pattern: str = "sequential"
    ):
        """
        Create a team of agents.
        
        Args:
            agents: List of Agent instances
            pattern: "sequential", "hierarchical", "swarm", or "round_robin"
        """
        self.agents = agents
        self.pattern = pattern
        self._logger = logging.getLogger(__name__)
        
        # Convert to AAF agents
        self._aaf_agents = [self._convert_to_aaf_agent(a) for a in agents]
        
        # Create pattern
        if pattern == "sequential":
            self._orchestrator = SequentialPattern(agents=self._aaf_agents)
        elif pattern == "hierarchical":
            self._orchestrator = HierarchicalPattern(
                manager_agent=self._aaf_agents[0],
                worker_agents=self._aaf_agents[1:]
            )
        elif pattern == "swarm":
            self._orchestrator = SwarmPattern(agents=self._aaf_agents)
        else:
            raise ValueError(f"Unknown pattern: {pattern}")
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the team."""
        result = self._orchestrator.execute(
            agents=[],
            initial_state={"request": task}
        )
        
        # Simplify output
        return {
            "status": "success" if result.get("response") else "error",
            "result": result.get("response"),
            "execution_time": result.get("execution_time", 0)
        }
    
    def _convert_to_aaf_agent(self, agent: Agent):
        """Convert simplified Agent to AAF protocol agent."""
        class AAFAgentAdapter:
            def __init__(self, simple_agent):
                self.simple_agent = simple_agent
            
            @property
            def agent_id(self):
                return self.simple_agent.name
            
            def initialize(self, config):
                pass
            
            def execute(self, input_data):
                return self.simple_agent.run(input_data)
            
            def shutdown(self):
                pass
        
        return AAFAgentAdapter(agent)


class HumanApproval:
    """
    Simplified human-in-the-loop interface.
    
    Example:
        >>> approval = HumanApproval()
        >>> if approval.required("Delete 100 records"):
        ...     approval.request("Are you sure?")
    """
    
    def __init__(self):
        self._workflow = ApprovalWorkflow()
    
    def request(self, question: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Request human approval.
        
        Returns:
            True if approved, False otherwise
        """
        status = self._workflow.request_approval(
            action=question,
            context=context or {}
        )
        return status.value == "approved"


class Safety:
    """
    Simplified safety/guardrails interface.
    
    Example:
        >>> safety = Safety()
        >>> safety.add_rule("No bulk deletes", lambda action: action.get("count", 0) > 100)
        >>> if safety.validate({"action": "delete", "count": 200}):
        ...     print("Action is safe")
    """
    
    def __init__(self):
        self._rules = []
        self._validator = None
    
    def add_rule(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: str = "high"
    ):
        """Add a safety rule."""
        self._rules.append({
            "name": name,
            "condition": condition,
            "message": f"Safety rule violated: {name}",
            "severity": severity
        })
        self._validator = GuardrailValidator(rules=self._rules)
    
    def validate(self, action: Dict[str, Any]) -> bool:
        """
        Validate an action against safety rules.
        
        Returns:
            True if action is safe, False if it violates rules
        """
        if not self._validator:
            return True
        return self._validator.validate(action)
    
    def get_violations(self) -> List[str]:
        """Get list of rule violations."""
        if not self._validator:
            return []
        violations = self._validator.get_violations()
        return [v["message"] for v in violations]


# Convenience factory functions
def create_agent(name: str) -> Agent:
    """Create a simple agent."""
    return Agent(name)


def create_memory(max_size: int = 100) -> Memory:
    """Create a memory system."""
    return Memory(max_size)


def create_team(agents: List[Agent], pattern: str = "sequential") -> Team:
    """Create a team of agents."""
    return Team(agents, pattern)


def create_planner() -> Planner:
    """Create a task planner."""
    return Planner()
