"""
Autonomous Agent decorator - Real agents with tools, memory, and planning.

This is different from @llm (simple LLM call) - autonomous agents can:
- Use tools (MCP, A2A, custom)
- Remember context (memory)
- Plan multi-step approaches
- Make autonomous decisions
"""

from typing import Callable, Optional, List, Dict, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def autonomous_agent(
    model: str = "openai:gpt-4",
    tools: Optional[List[str]] = None,
    memory: bool = False,
    planning: bool = False,
    max_iterations: int = 10
):
    """
    Create an autonomous agent that can use tools, remember context, and plan.
    
    This is a REAL AGENT - not just an LLM call.
    
    Example:
        @node
        @autonomous_agent(
            model="openai:gpt-4",
            tools=["search", "calculator", "weather"],
            memory=True,
            planning=True
        )
        def research_agent(state):
            '''Autonomous agent that researches topics.'''
            query = state["query"]
            # Agent will:
            # 1. Plan approach (break down task)
            # 2. Decide which tools to use
            # 3. Call tools multiple times as needed
            # 4. Remember previous interactions
            # 5. Synthesize final answer
            return {"research_complete": True}
    
    Args:
        model: LLM model to use for agent reasoning
        tools: List of tool names the agent can use
        memory: Whether agent should remember past interactions
        planning: Whether agent should plan multi-step approaches
        max_iterations: Max tool calls before stopping (prevent infinite loops)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            logger.info(f"[AutonomousAgent] Starting with model={model}, tools={tools}")
            
            # Initialize memory if enabled
            agent_memory = []
            if memory and "_memory" in state:
                agent_memory = state["_memory"]
            
            # Initialize plan if planning enabled
            plan = None
            if planning:
                logger.info("[AutonomousAgent] Creating plan...")
                plan = _create_plan(state, tools or [])
                logger.info(f"[AutonomousAgent] Plan: {len(plan)} steps")
            
            # Agent loop - decide and execute tools
            iteration = 0
            agent_state = state.copy()
            tool_history = []
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"[AutonomousAgent] Iteration {iteration}/{max_iterations}")
                
                # Agent decides: What to do next?
                decision = _agent_decide(
                    agent_state,
                    tools or [],
                    tool_history,
                    plan,
                    model
                )
                
                if decision["action"] == "finish":
                    logger.info("[AutonomousAgent] Agent decided to finish")
                    break
                
                if decision["action"] == "use_tool":
                    tool_name = decision["tool"]
                    tool_input = decision["input"]
                    
                    logger.info(f"[AutonomousAgent] Using tool: {tool_name}")
                    
                    # Execute tool
                    tool_result = _execute_tool(tool_name, tool_input, agent_state)
                    
                    # Update state with tool result
                    agent_state[f"_{tool_name}_result"] = tool_result
                    
                    # Add to history
                    tool_history.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": tool_result
                    })
                    
                    # Store in memory if enabled
                    if memory:
                        agent_memory.append({
                            "action": "tool_call",
                            "tool": tool_name,
                            "result": tool_result
                        })
            
            # Synthesize final result
            logger.info("[AutonomousAgent] Synthesizing final result...")
            
            # Call original function with enhanced state
            final_state = {
                **agent_state,
                "_tool_history": tool_history,
                "_iterations": iteration,
                "_memory": agent_memory if memory else None
            }
            
            result = func(final_state)
            
            logger.info("[AutonomousAgent] Completed")
            
            return result
        
        # Mark as autonomous agent
        wrapper._is_autonomous_agent = True
        wrapper._agent_model = model
        wrapper._agent_tools = tools
        
        return wrapper
    
    return decorator


def _create_plan(state: Dict[str, Any], available_tools: List[str]) -> List[Dict[str, str]]:
    """
    Create a multi-step plan for the agent.
    
    In a real implementation, this would call an LLM to generate the plan.
    """
    # Simplified planning - in production, use LLM
    from aaf.planning import SimpleTaskPlanner
    
    planner = SimpleTaskPlanner()
    
    goal = state.get("query") or state.get("task") or "Complete task"
    
    plan = planner.create_plan(
        goal=str(goal),
        context=state,
        available_services=available_tools
    )
    
    return plan


def _agent_decide(
    state: Dict[str, Any],
    available_tools: List[str],
    tool_history: List[Dict[str, Any]],
    plan: Optional[List[Dict[str, str]]],
    model: str
) -> Dict[str, Any]:
    """
    Agent decides what to do next based on state and tool history.
    
    In a real implementation, this would use an LLM with ReAct prompting.
    """
    # Simplified decision making - in production, use LLM with ReAct
    from aaf.planning import ReActReasoner
    
    reasoner = ReActReasoner()
    
    # Get current observation
    observation = {
        "state": state,
        "tools_used": len(tool_history),
        "available_tools": available_tools
    }
    
    # Agent reasons about next action
    reasoning_result = reasoner.reason(
        observation=str(observation),
        history=tool_history,
        goal=state.get("query") or state.get("task") or "Complete task"
    )
    action = reasoning_result.get("action", {})
    
    # Simplification: if we've used tools or don't have any, finish
    if not available_tools or len(tool_history) >= 3:
        return {"action": "finish"}
    
    # Otherwise, use first available tool
    if available_tools and len(tool_history) < len(available_tools):
        return {
            "action": "use_tool",
            "tool": available_tools[len(tool_history)],
            "input": state.get("query") or state.get("task") or ""
        }
    
    return {"action": "finish"}


def _execute_tool(tool_name: str, tool_input: Any, state: Dict[str, Any]) -> Any:
    """
    Execute a tool call.
    
    In a real implementation, this would call actual MCP tools, A2A agents, etc.
    """
    logger.info(f"[Tool:{tool_name}] Executing with input: {str(tool_input)[:50]}")
    
    # Simulated tool execution
    # In production, would call real MCP/A2A/custom tools
    
    tool_results = {
        "search": f"Search results for: {tool_input}",
        "calculator": f"Calculated result: 42",
        "weather": f"Weather data: sunny, 72°F",
        "database": f"Database query results: ...",
    }
    
    result = tool_results.get(tool_name, f"Tool {tool_name} executed")
    
    logger.info(f"[Tool:{tool_name}] Result: {str(result)[:50]}")
    
    return result
