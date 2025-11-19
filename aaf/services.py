"""
Service implementations for external protocol integrations.

This module provides concrete implementations of AbstractService for MCP and A2A protocols,
including dummy clients for demonstration purposes.
"""

from typing import Dict, Any, Optional
from aaf.abstracts import AbstractService


class DummyMCPClient:
    """
    Dummy MCP (Model Context Protocol) client for demonstration.
    
    Simulates an MCP tool service that can execute with optional authentication.
    """
    
    def __init__(self, tool_name: str = "search"):
        self.tool_name = tool_name
    
    def call_tool(self, params: Dict[str, Any], auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate calling an MCP tool.
        
        Args:
            params: Tool parameters
            auth_token: Optional authentication token
            
        Returns:
            Simulated tool response
        """
        if auth_token:
            return {
                "status": "success",
                "tool": self.tool_name,
                "result": f"MCP tool '{self.tool_name}' executed successfully with authentication",
                "data": params,
                "authenticated": True,
                "token_used": auth_token[:10] + "..." if len(auth_token) > 10 else auth_token
            }
        else:
            return {
                "status": "success",
                "tool": self.tool_name,
                "result": f"MCP tool '{self.tool_name}' executed without authentication",
                "data": params,
                "authenticated": False
            }


class DummyA2AClient:
    """
    Dummy A2A (Agent-to-Agent) client for demonstration.
    
    Simulates an A2A protocol client that requires authentication.
    """
    
    def __init__(self, target_agent: str = "assistant_agent"):
        self.target_agent = target_agent
    
    def delegate_task(self, task: Dict[str, Any], auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate delegating a task to another agent via A2A protocol.
        
        Args:
            task: Task specification
            auth_token: Authentication token (REQUIRED for A2A)
            
        Returns:
            Delegation response
            
        Raises:
            PermissionError: If auth_token is not provided
        """
        if not auth_token:
            raise PermissionError(
                f"A2A delegation to '{self.target_agent}' requires authentication token. "
                "No token provided in request."
            )
        
        return {
            "status": "delegated",
            "target_agent": self.target_agent,
            "task": task,
            "result": f"Task successfully delegated to {self.target_agent}",
            "authenticated": True,
            "token_used": auth_token[:10] + "..." if len(auth_token) > 10 else auth_token
        }


class MCPToolService:
    """
    MCP Tool Service implementation.
    
    Wraps the dummy MCP client to provide a standardized service interface.
    Can optionally require tokens for secure MCP operations.
    """
    
    def __init__(self, tool_name: str = "search", require_auth: bool = False):
        self._client = DummyMCPClient(tool_name)
        self._service_name = f"mcp_tool_{tool_name}"
        self._require_auth = require_auth
    
    @property
    def service_name(self) -> str:
        return self._service_name
    
    @property
    def requires_token(self) -> bool:
        return self._require_auth
    
    def execute(self, request: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute an MCP tool call.
        
        Args:
            request: Request containing tool parameters
            token: Optional authentication token
            
        Returns:
            MCP tool response
            
        Raises:
            PermissionError: If token is required but not provided
        """
        if self.requires_token and not token:
            raise PermissionError(
                f"Service '{self.service_name}' requires authentication token, but none was provided."
            )
        
        params = request.get("params", {})
        return self._client.call_tool(params, token)


class A2AClientService:
    """
    A2A Client Service implementation.
    
    Wraps the dummy A2A client to provide a standardized service interface.
    Always requires authentication tokens for agent delegation.
    """
    
    def __init__(self, target_agent: str = "assistant_agent"):
        self._client = DummyA2AClient(target_agent)
        self._service_name = f"a2a_client_{target_agent}"
    
    @property
    def service_name(self) -> str:
        return self._service_name
    
    @property
    def requires_token(self) -> bool:
        return True
    
    def execute(self, request: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute an A2A delegation.
        
        Args:
            request: Request containing task specification
            token: Authentication token (REQUIRED)
            
        Returns:
            A2A delegation response
            
        Raises:
            PermissionError: If token is not provided (delegated from DummyA2AClient)
        """
        if not token:
            raise PermissionError(
                f"Service '{self.service_name}' requires authentication token for A2A delegation. "
                "No token was provided."
            )
        
        task = request.get("task", {})
        return self._client.delegate_task(task, token)
