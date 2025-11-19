"""
Planning and reasoning implementations for the Agentic Application Framework.

This module provides concrete implementations of planners and reasoners that
enable agents to decompose complex tasks and make decisions using patterns
like ReAct (Reason + Act).
"""

import logging
import time
from typing import Any, Dict, List, Optional
from aaf.abstracts import AbstractPlanner, AbstractReasoner


class SimpleTaskPlanner:
    """
    Simple task planner that decomposes goals into executable steps.
    
    For production use with LLMs, integrate with model APIs to generate
    plans dynamically based on context.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the task planner.
        
        Args:
            logger: Logger instance for debugging
        """
        self._logger = logger or logging.getLogger(__name__)
        self._plan_history: List[Dict[str, Any]] = []
        self._logger.info("[TaskPlanner] Initialized")
    
    @property
    def planner_name(self) -> str:
        return "simple_task_planner"
    
    def create_plan(
        self,
        goal: str,
        context: Dict[str, Any],
        available_services: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Create an execution plan by breaking down the goal.
        
        This is a rule-based implementation. For LLM-driven planning,
        integrate with OpenAI/Anthropic APIs.
        """
        self._logger.info(f"[TaskPlanner] Creating plan for goal: {goal}")
        
        plan = []
        plan_id = f"plan_{int(time.time())}"
        
        keywords_to_services = {
            "search": "mcp_tool_search",
            "weather": "mcp_tool_weather",
            "data": "mcp_tool_database",
            "agent": "a2a_client",
            "delegate": "a2a_client",
            "assistant": "a2a_client"
        }
        
        goal_lower = goal.lower()
        
        for keyword, service in keywords_to_services.items():
            if keyword in goal_lower and service in available_services:
                step = {
                    "step_id": f"{plan_id}_step_{len(plan) + 1}",
                    "action": service,
                    "description": f"Use {service} to help achieve: {goal}",
                    "parameters": {
                        "query": goal,
                        "context": context
                    },
                    "depends_on": []
                }
                plan.append(step)
        
        if not plan:
            if available_services:
                step = {
                    "step_id": f"{plan_id}_step_1",
                    "action": available_services[0],
                    "description": f"Execute {available_services[0]} for: {goal}",
                    "parameters": {
                        "query": goal,
                        "context": context
                    },
                    "depends_on": []
                }
                plan.append(step)
            else:
                self._logger.warning("[TaskPlanner] No services available for planning")
        
        plan_record = {
            "plan_id": plan_id,
            "goal": goal,
            "steps": plan,
            "created_at": time.time()
        }
        self._plan_history.append(plan_record)
        
        self._logger.info(f"[TaskPlanner] Created plan with {len(plan)} steps")
        return plan
    
    def refine_plan(
        self,
        plan: List[Dict[str, Any]],
        feedback: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Refine an existing plan based on feedback.
        
        Args:
            plan: Current execution plan
            feedback: Feedback containing results, errors, or suggestions
        """
        self._logger.info(f"[TaskPlanner] Refining plan with {len(plan)} steps")
        
        refined_plan = []
        
        if feedback.get("status") == "error":
            error_msg = feedback.get("error", "")
            
            if "permission" in error_msg.lower() or "auth" in error_msg.lower():
                for step in plan:
                    refined_step = step.copy()
                    refined_step["parameters"]["require_auth"] = True
                    refined_plan.append(refined_step)
                
                self._logger.info("[TaskPlanner] Added authentication requirement to plan")
            
            elif "not found" in error_msg.lower() or "missing" in error_msg.lower():
                for step in plan:
                    if step not in refined_plan:
                        refined_plan.append(step.copy())
                
                self._logger.info("[TaskPlanner] Plan unchanged, issue may be external")
            
            else:
                refined_plan = plan
                self._logger.warning("[TaskPlanner] Unable to refine plan based on feedback")
        
        elif feedback.get("status") == "partial_success":
            successful_steps = feedback.get("completed_steps", [])
            
            for step in plan:
                if step.get("step_id") not in successful_steps:
                    refined_plan.append(step.copy())
            
            self._logger.info(f"[TaskPlanner] Retained {len(refined_plan)} incomplete steps")
        
        else:
            refined_plan = plan
            self._logger.info("[TaskPlanner] Plan completed successfully, no refinement needed")
        
        return refined_plan
    
    def get_plan_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all created plans.
        
        Returns:
            List of plan records with metadata
        """
        return self._plan_history.copy()


class ReActReasoner:
    """
    Reasoning engine implementing the ReAct pattern (Reason + Act).
    
    ReAct alternates between reasoning about the current state and
    taking actions, enabling step-by-step problem solving.
    
    For LLM-driven reasoning, integrate with model APIs.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the ReAct reasoner.
        
        Args:
            logger: Logger instance for debugging
        """
        self._logger = logger or logging.getLogger(__name__)
        self._reasoning_history: List[Dict[str, Any]] = []
        self._logger.info("[ReActReasoner] Initialized")
    
    @property
    def reasoner_name(self) -> str:
        return "react_reasoner"
    
    def reason(
        self,
        observation: str,
        history: List[Dict[str, Any]],
        goal: str
    ) -> Dict[str, Any]:
        """
        Reason about the current state using the ReAct pattern.
        
        The ReAct pattern consists of:
        1. Thought: Reasoning about what to do next
        2. Action: Deciding which action to take
        3. Observation: Processing the result of the action
        
        This is a rule-based implementation. For LLM-driven reasoning,
        integrate with model APIs.
        """
        self._logger.info(f"[ReActReasoner] Reasoning for goal: {goal}")
        
        thought = self._generate_thought(observation, history, goal)
        action = self._determine_action(thought, observation, history)
        
        reasoning_step = {
            "timestamp": time.time(),
            "goal": goal,
            "observation": observation,
            "thought": thought,
            "action": action,
            "step_number": len(history) + 1
        }
        
        self._reasoning_history.append(reasoning_step)
        
        self._logger.info(f"[ReActReasoner] Thought: {thought}")
        self._logger.info(f"[ReActReasoner] Action: {action['type']}")
        
        return reasoning_step
    
    def _generate_thought(
        self,
        observation: str,
        history: List[Dict[str, Any]],
        goal: str
    ) -> str:
        """Generate reasoning about the current state."""
        
        if not history:
            return f"I need to start working on the goal: {goal}. First step is to analyze what's needed."
        
        if "success" in observation.lower():
            return f"The previous action was successful. I should continue toward the goal: {goal}."
        
        if "error" in observation.lower() or "failed" in observation.lower():
            return f"The previous action failed. I need to adjust my approach to achieve: {goal}."
        
        if "permission" in observation.lower() or "auth" in observation.lower():
            return "The action failed due to authentication issues. I need to ensure proper credentials are provided."
        
        return f"Continuing to work toward the goal: {goal}. Analyzing the latest observation."
    
    def _determine_action(
        self,
        thought: str,
        observation: str,
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine the next action based on reasoning."""
        
        if "authentication" in thought.lower() or "credentials" in thought.lower():
            return {
                "type": "request_auth",
                "description": "Request authentication credentials",
                "parameters": {}
            }
        
        if "failed" in thought.lower() or "adjust" in thought.lower():
            return {
                "type": "retry_with_modification",
                "description": "Retry previous action with modifications",
                "parameters": {"retry_count": len([h for h in history if h.get("action", {}).get("type") == "retry_with_modification"]) + 1}
            }
        
        if "successful" in thought.lower() or "continue" in thought.lower():
            return {
                "type": "proceed_next_step",
                "description": "Continue to next step in the plan",
                "parameters": {}
            }
        
        return {
            "type": "execute_plan",
            "description": "Execute the planned action",
            "parameters": {}
        }
    
    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all reasoning steps.
        
        Returns:
            List of reasoning records with thoughts and actions
        """
        return self._reasoning_history.copy()
    
    def summarize_reasoning(self) -> str:
        """
        Summarize the reasoning process as a narrative.
        
        Returns:
            Human-readable summary of the reasoning chain
        """
        if not self._reasoning_history:
            return "No reasoning steps recorded yet."
        
        summary_parts = []
        for step in self._reasoning_history:
            summary_parts.append(
                f"Step {step['step_number']}: {step['thought']} "
                f"→ Action: {step['action']['description']}"
            )
        
        return "\n".join(summary_parts)
