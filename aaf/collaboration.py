"""
Multi-agent collaboration patterns for the Agentic Application Framework.

This module provides collaboration patterns inspired by leading frameworks
like CrewAI, AutoGen, and LangGraph for coordinating multiple agents.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Callable
from aaf.abstracts import AbstractAgent, AbstractState


class CollaborationPattern:
    """Base class for multi-agent collaboration patterns."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the collaboration pattern.
        
        Args:
            logger: Logger instance for debugging
        """
        self._logger = logger or logging.getLogger(__name__)
    
    def execute(
        self,
        agents: List[AbstractAgent],
        initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the collaboration pattern.
        
        Args:
            agents: List of agents to coordinate
            initial_state: Initial state for the collaboration
            
        Returns:
            Final state after collaboration
        """
        raise NotImplementedError("Subclasses must implement execute()")


class HierarchicalPattern(CollaborationPattern):
    """
    Hierarchical collaboration pattern (Manager-Worker).
    
    A manager agent delegates tasks to specialized worker agents,
    aggregates results, and makes final decisions.
    
    Inspired by: LangGraph supervisor pattern, AutoGen hierarchical agents
    """
    
    def __init__(
        self,
        manager_agent: AbstractAgent,
        worker_agents: List[AbstractAgent],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize hierarchical collaboration.
        
        Args:
            manager_agent: The manager/coordinator agent
            worker_agents: List of specialized worker agents
            logger: Logger instance for debugging
        """
        super().__init__(logger)
        self._manager = manager_agent
        self._workers = worker_agents
        self._logger.info(
            f"[HierarchicalPattern] Initialized with 1 manager and {len(worker_agents)} workers"
        )
    
    def execute(
        self,
        agents: List[AbstractAgent],
        initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute hierarchical collaboration.
        
        Flow:
        1. Manager analyzes the task
        2. Manager delegates to appropriate workers
        3. Workers execute their specialized tasks
        4. Manager aggregates and finalizes results
        """
        self._logger.info("[HierarchicalPattern] Starting hierarchical execution")
        
        state = initial_state.copy()
        state["collaboration_pattern"] = "hierarchical"
        state["start_time"] = time.time()
        
        manager_input = {
            "task": state.get("request", {}),
            "available_workers": [w.agent_id for w in self._workers],
            "phase": "delegation"
        }
        
        self._logger.info(f"[HierarchicalPattern] Manager delegating tasks...")
        manager_delegation = self._manager.execute(manager_input)
        
        worker_results = []
        delegated_tasks = manager_delegation.get("delegated_tasks", [])
        
        if not delegated_tasks:
            delegated_tasks = [{"worker": w.agent_id, "task": state.get("request", {})} for w in self._workers]
        
        for task in delegated_tasks:
            worker_id = task.get("worker")
            worker = next((w for w in self._workers if w.agent_id == worker_id), None)
            
            if worker:
                self._logger.info(f"[HierarchicalPattern] Executing task on worker: {worker_id}")
                try:
                    result = worker.execute(task.get("task", {}))
                    worker_results.append({
                        "worker_id": worker_id,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    self._logger.error(f"[HierarchicalPattern] Worker {worker_id} failed: {str(e)}")
                    worker_results.append({
                        "worker_id": worker_id,
                        "status": "error",
                        "error": str(e)
                    })
        
        aggregation_input = {
            "worker_results": worker_results,
            "original_task": state.get("request", {}),
            "phase": "aggregation"
        }
        
        self._logger.info(f"[HierarchicalPattern] Manager aggregating {len(worker_results)} results...")
        final_result = self._manager.execute(aggregation_input)
        
        state["response"] = final_result
        state["worker_results"] = worker_results
        state["execution_time"] = time.time() - state["start_time"]
        
        self._logger.info("[HierarchicalPattern] Hierarchical execution completed")
        return state


class SequentialPattern(CollaborationPattern):
    """
    Sequential collaboration pattern (Pipeline).
    
    Agents execute in a defined sequence, each building on the
    previous agent's output. Common for workflows like
    Research → Write → Review.
    
    Inspired by: CrewAI task sequences, LangChain chains
    """
    
    def __init__(
        self,
        agents: List[AbstractAgent],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize sequential collaboration.
        
        Args:
            agents: List of agents in execution order
            logger: Logger instance for debugging
        """
        super().__init__(logger)
        self._agents = agents
        self._logger.info(f"[SequentialPattern] Initialized with {len(agents)} agents")
    
    def execute(
        self,
        agents: List[AbstractAgent],
        initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute sequential collaboration.
        
        Flow:
        1. Agent 1 processes initial input
        2. Agent 2 processes Agent 1's output
        3. Agent 3 processes Agent 2's output
        4. ... and so on
        """
        self._logger.info("[SequentialPattern] Starting sequential execution")
        
        state = initial_state.copy()
        state["collaboration_pattern"] = "sequential"
        state["start_time"] = time.time()
        state["execution_chain"] = []
        
        current_input = state.get("request", {})
        
        agents_to_use = agents if agents else self._agents
        
        for i, agent in enumerate(agents_to_use):
            self._logger.info(f"[SequentialPattern] Executing step {i + 1}/{len(agents_to_use)}: {agent.agent_id}")
            
            try:
                result = agent.execute(current_input)
                
                state["execution_chain"].append({
                    "step": i + 1,
                    "agent_id": agent.agent_id,
                    "status": "success",
                    "output": result
                })
                
                current_input = result
                
            except Exception as e:
                self._logger.error(f"[SequentialPattern] Agent {agent.agent_id} failed: {str(e)}")
                state["execution_chain"].append({
                    "step": i + 1,
                    "agent_id": agent.agent_id,
                    "status": "error",
                    "error": str(e)
                })
                break
        
        state["response"] = current_input
        state["execution_time"] = time.time() - state["start_time"]
        
        self._logger.info("[SequentialPattern] Sequential execution completed")
        return state


class SwarmPattern(CollaborationPattern):
    """
    Swarm collaboration pattern (Parallel Autonomous).
    
    Multiple agents work autonomously in parallel on different
    aspects of a problem, with automatic handoffs and coordination.
    
    Inspired by: OpenAI Swarm, AutoGen swarm agents
    """
    
    def __init__(
        self,
        agents: List[AbstractAgent],
        handoff_function: Optional[Callable] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize swarm collaboration.
        
        Args:
            agents: List of autonomous agents
            handoff_function: Optional function to determine handoffs
            logger: Logger instance for debugging
        """
        super().__init__(logger)
        self._agents = agents
        self._handoff_function = handoff_function or self._default_handoff
        self._logger.info(f"[SwarmPattern] Initialized with {len(agents)} agents")
    
    def execute(
        self,
        agents: List[AbstractAgent],
        initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute swarm collaboration.
        
        Flow:
        1. All agents attempt their specialized tasks in parallel
        2. Results are collected and aggregated
        3. Handoffs occur if agents need to collaborate
        """
        self._logger.info("[SwarmPattern] Starting swarm execution")
        
        state = initial_state.copy()
        state["collaboration_pattern"] = "swarm"
        state["start_time"] = time.time()
        state["agent_outputs"] = []
        
        agents_to_use = agents if agents else self._agents
        
        import concurrent.futures
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents_to_use)) as executor:
            futures = {}
            
            for agent in agents_to_use:
                task = state.get("request", {}).copy()
                task["agent_role"] = agent.agent_id
                
                future = executor.submit(self._execute_agent, agent, task)
                futures[future] = agent
            
            for future in concurrent.futures.as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    state["agent_outputs"].append({
                        "agent_id": agent.agent_id,
                        "status": "success",
                        "output": result
                    })
                    self._logger.info(f"[SwarmPattern] Agent {agent.agent_id} completed successfully")
                except Exception as e:
                    self._logger.error(f"[SwarmPattern] Agent {agent.agent_id} failed: {str(e)}")
                    state["agent_outputs"].append({
                        "agent_id": agent.agent_id,
                        "status": "error",
                        "error": str(e)
                    })
        
        state["response"] = self._aggregate_swarm_results(state["agent_outputs"])
        state["execution_time"] = time.time() - state["start_time"]
        
        self._logger.info("[SwarmPattern] Swarm execution completed")
        return state
    
    def _execute_agent(self, agent: AbstractAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent with error handling."""
        return agent.execute(task)
    
    def _default_handoff(self, from_agent: str, result: Dict[str, Any]) -> Optional[str]:
        """Default handoff logic - no automatic handoffs."""
        return None
    
    def _aggregate_swarm_results(self, outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from all swarm agents."""
        successful_outputs = [o for o in outputs if o.get("status") == "success"]
        
        if not successful_outputs:
            return {
                "status": "all_failed",
                "error": "All agents in the swarm failed to complete their tasks"
            }
        
        return {
            "status": "success",
            "swarm_results": successful_outputs,
            "successful_count": len(successful_outputs),
            "total_count": len(outputs)
        }


class RoundRobinPattern(CollaborationPattern):
    """
    Round-robin collaboration pattern.
    
    Agents take turns processing the task until completion or
    a stop condition is met. Useful for iterative refinement.
    """
    
    def __init__(
        self,
        agents: List[AbstractAgent],
        max_iterations: int = 5,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize round-robin collaboration.
        
        Args:
            agents: List of agents to rotate through
            max_iterations: Maximum number of iterations
            logger: Logger instance for debugging
        """
        super().__init__(logger)
        self._agents = agents
        self._max_iterations = max_iterations
        self._logger.info(f"[RoundRobinPattern] Initialized with {len(agents)} agents, max {max_iterations} iterations")
    
    def execute(
        self,
        agents: List[AbstractAgent],
        initial_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute round-robin collaboration.
        
        Each agent refines the output until done or max iterations reached.
        """
        self._logger.info("[RoundRobinPattern] Starting round-robin execution")
        
        state = initial_state.copy()
        state["collaboration_pattern"] = "round_robin"
        state["start_time"] = time.time()
        state["iterations"] = []
        
        current_result = state.get("request", {})
        agents_to_use = agents if agents else self._agents
        
        for iteration in range(self._max_iterations):
            for i, agent in enumerate(agents_to_use):
                self._logger.info(
                    f"[RoundRobinPattern] Iteration {iteration + 1}, Agent {i + 1}/{len(agents_to_use)}: {agent.agent_id}"
                )
                
                try:
                    result = agent.execute(current_result)
                    
                    state["iterations"].append({
                        "iteration": iteration + 1,
                        "agent_id": agent.agent_id,
                        "status": "success",
                        "output": result
                    })
                    
                    current_result = result
                    
                    if result.get("status") == "complete":
                        self._logger.info("[RoundRobinPattern] Completion detected, stopping early")
                        state["response"] = current_result
                        state["execution_time"] = time.time() - state["start_time"]
                        return state
                    
                except Exception as e:
                    self._logger.error(f"[RoundRobinPattern] Agent {agent.agent_id} failed: {str(e)}")
                    state["iterations"].append({
                        "iteration": iteration + 1,
                        "agent_id": agent.agent_id,
                        "status": "error",
                        "error": str(e)
                    })
        
        state["response"] = current_result
        state["execution_time"] = time.time() - state["start_time"]
        
        self._logger.info("[RoundRobinPattern] Round-robin execution completed")
        return state
