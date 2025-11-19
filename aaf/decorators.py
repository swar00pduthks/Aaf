"""
Simple decorators for zero-boilerplate agent creation.

This is AAF's standout feature: Lambda-like simplicity for creating
agents from any framework or custom functions.
"""

from typing import Callable, Optional, Dict, Any
from functools import wraps
import logging


# Global registry of decorated agents
_AGENT_REGISTRY: Dict[str, Any] = {}


def agent(
    agent_id: Optional[str] = None,
    framework: Optional[str] = None
):
    """
    Decorator to turn any function into an AAF agent.
    
    Zero boilerplate - just decorate and go!
    
    Examples:
        @agent
        def researcher(query: str) -> str:
            return search_and_analyze(query)
        
        @agent(agent_id="custom_analyzer")
        def analyze(data: dict) -> dict:
            return process(data)
        
        @agent(framework="langgraph")
        def lg_agent(input_data):
            return langgraph_instance.invoke(input_data)
    """
    # Handle both @agent and @agent() syntax
    if callable(agent_id):
        # Called as @agent without parentheses
        func = agent_id
        agent_id = None
        return _create_agent(func, None, None)
    
    def decorator(func: Callable):
        return _create_agent(func, agent_id, framework)
    
    return decorator


def _create_agent(func: Callable, agent_id: Optional[str], framework: Optional[str]):
    """Internal function to create agent from function."""
    # Use function name as agent_id if not provided
    _agent_id = agent_id or func.__name__
    
    # Create agent wrapper
    class DecoratedAgent:
        def __init__(self):
            self._func = func
            self._id = _agent_id
            self._framework = framework
        
        @property
        def agent_id(self):
            return self._id
        
        def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            # Extract the right parameter based on framework
            if framework == "langgraph":
                param = input_data
            elif framework == "crewai":
                param = input_data.get("task", input_data)
            else:
                # Default: pass query or full dict
                param = input_data.get("query", input_data)
            
            # Execute the function
            result = self._func(param)
            
            return {
                "status": "success",
                "result": result,
                "agent_id": self._id
            }
        
        def initialize(self, config): pass
        def shutdown(self): pass
        
        def __call__(self, *args, **kwargs):
            """Allow calling the original function directly."""
            return self._func(*args, **kwargs)
        
        def __repr__(self):
            return f"<Agent '{self._id}' framework={self._framework or 'custom'}>"
    
    # Create and register agent
    agent_instance = DecoratedAgent()
    _AGENT_REGISTRY[_agent_id] = agent_instance
    
    # Return the agent instance (can still call as function)
    return agent_instance


def langgraph_agent(agent_id: Optional[str] = None):
    """
    Decorator specifically for LangGraph agents.
    
    Example:
        @langgraph_agent
        def my_lg_agent(messages):
            return langgraph_instance.invoke(messages)
    """
    return agent(agent_id=agent_id, framework="langgraph")


def crewai_agent(agent_id: Optional[str] = None):
    """
    Decorator specifically for CrewAI agents.
    
    Example:
        @crewai_agent
        def my_crew_agent(task):
            return crew_instance.kickoff()
    """
    return agent(agent_id=agent_id, framework="crewai")


def microsoft_agent(agent_id: Optional[str] = None):
    """
    Decorator specifically for Microsoft Agent Framework.
    
    Example:
        @microsoft_agent
        def my_ms_agent(query):
            return ms_agent_instance.run(query)
    """
    return agent(agent_id=agent_id, framework="microsoft")


def workflow(*agents, pattern: str = "sequential"):
    """
    Decorator to create a workflow from multiple agents.
    
    Example:
        @workflow(researcher, analyzer, writer, pattern="sequential")
        def research_pipeline(query: str):
            # Automatically orchestrates the 3 agents!
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from aaf.collaboration import SequentialPattern, HierarchicalPattern
            
            # Create pattern
            if pattern == "sequential":
                orchestrator = SequentialPattern(agents=list(agents))
            elif pattern == "hierarchical":
                orchestrator = HierarchicalPattern(
                    manager_agent=agents[0],
                    worker_agents=list(agents[1:])
                )
            else:
                raise ValueError(f"Unknown pattern: {pattern}")
            
            # Get input
            initial_input = args[0] if args else kwargs
            
            # Execute workflow
            result = orchestrator.execute(
                agents=[],
                initial_state={"request": initial_input}
            )
            
            return result
        
        return wrapper
    
    return decorator


def get_agent(agent_id: str):
    """Get a registered agent by ID."""
    return _AGENT_REGISTRY.get(agent_id)


def list_agents():
    """List all registered agents."""
    return list(_AGENT_REGISTRY.keys())
