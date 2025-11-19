"""
Tool decorators for AAF - MCP tools, A2A agents, and custom tools.

Provides simple decorators for integrating external tools and services.
"""

from typing import Callable, Optional, Dict, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def mcp_tool(
    tool_name: str,
    require_auth: bool = False,
    api_key: Optional[str] = None
):
    """
    Decorator to create an MCP (Model Context Protocol) tool.
    
    MCP tools are external services that agents can call (search, weather, database, etc.)
    
    Example:
        @node
        @mcp_tool("search")
        def search_web(state):
            query = state["query"]
            # MCP client handles the actual search
            return {"search_results": [...]}
        
        @node
        @mcp_tool("weather", require_auth=True)
        def get_weather(state):
            location = state["location"]
            return {"weather": "sunny"}
    
    Args:
        tool_name: Name of the MCP tool
        require_auth: Whether this tool requires authentication
        api_key: Optional API key for the tool
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            logger.info(f"[MCP:{tool_name}] Calling tool...")
            
            # In a real implementation, this would:
            # 1. Get MCP client
            # 2. Handle authentication if required
            # 3. Call the actual MCP tool
            # 4. Return results
            
            # For now, simulate MCP call
            from aaf.services import MCPToolService
            
            mcp_service = MCPToolService(
                tool_name=tool_name,
                require_auth=require_auth
            )
            
            # Extract request from state
            request = {"params": state}
            
            # Get token if required
            token = None
            if require_auth:
                token = state.get("_auth_token") or state.get("token_map", {}).get(f"mcp_tool_{tool_name}")
            
            try:
                # Execute MCP tool
                result = mcp_service.execute(request, token)
                
                logger.info(f"[MCP:{tool_name}] Success: {result.get('status')}")
                
                # Call original function with MCP result in state
                enhanced_state = {**state, "_mcp_result": result}
                return func(enhanced_state)
                
            except Exception as e:
                logger.error(f"[MCP:{tool_name}] Error: {e}")
                return {**state, "error": str(e), "failed_tool": tool_name}
        
        # Mark as MCP tool
        wrapper._is_mcp_tool = True
        wrapper._tool_name = tool_name
        
        return wrapper
    
    return decorator


def a2a_agent(
    target_agent: str,
    require_auth: bool = True
):
    """
    Decorator to delegate to another agent via A2A (Agent-to-Agent) protocol.
    
    A2A allows agents to delegate tasks to other specialized agents.
    
    Example:
        @node
        @a2a_agent("research_specialist")
        def delegate_research(state):
            task = state["research_task"]
            # A2A client delegates to research_specialist
            return {"research_results": {...}}
        
        @node
        @a2a_agent("code_reviewer", require_auth=True)
        def get_code_review(state):
            code = state["code"]
            return {"review": "..."}
    
    Args:
        target_agent: ID of the agent to delegate to
        require_auth: Whether A2A requires authentication (default True)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            logger.info(f"[A2A] Delegating to agent: {target_agent}")
            
            # In real implementation:
            # 1. Get A2A client
            # 2. Handle authentication
            # 3. Delegate task to target agent
            # 4. Wait for response
            # 5. Return results
            
            from aaf.services import A2AClientService
            
            a2a_service = A2AClientService(target_agent=target_agent)
            
            # Extract task from state
            request = {"task": state.get("task", state)}
            
            # Get token
            token = None
            if require_auth:
                token = state.get("_auth_token") or state.get("token_map", {}).get(f"a2a_client_{target_agent}")
            
            try:
                # Execute A2A delegation
                result = a2a_service.execute(request, token)
                
                logger.info(f"[A2A] Delegation to {target_agent} successful")
                
                # Call original function with A2A result
                enhanced_state = {**state, "_a2a_result": result}
                return func(enhanced_state)
                
            except Exception as e:
                logger.error(f"[A2A] Delegation failed: {e}")
                return {**state, "error": str(e), "failed_delegation": target_agent}
        
        # Mark as A2A delegation
        wrapper._is_a2a_agent = True
        wrapper._target_agent = target_agent
        
        return wrapper
    
    return decorator


def custom_tool(
    tool_name: str,
    executor: Callable
):
    """
    Decorator to create a custom tool (not MCP or A2A).
    
    Example:
        def calculate(params):
            return {"result": params["a"] + params["b"]}
        
        @node
        @custom_tool("calculator", executor=calculate)
        def do_calculation(state):
            a = state["num1"]
            b = state["num2"]
            # Tool will execute calculation
            return {"sum": state["_tool_result"]["result"]}
    
    Args:
        tool_name: Name of the custom tool
        executor: Function that executes the tool
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            logger.info(f"[CustomTool:{tool_name}] Executing...")
            
            try:
                # Execute custom tool
                result = executor(state)
                
                logger.info(f"[CustomTool:{tool_name}] Success")
                
                # Call original function with tool result
                enhanced_state = {**state, "_tool_result": result}
                return func(enhanced_state)
                
            except Exception as e:
                logger.error(f"[CustomTool:{tool_name}] Error: {e}")
                return {**state, "error": str(e), "failed_tool": tool_name}
        
        wrapper._is_custom_tool = True
        wrapper._tool_name = tool_name
        
        return wrapper
    
    return decorator
