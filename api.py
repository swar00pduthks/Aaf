"""
FastAPI Service for Agentic Application Framework (AAF)

This service exposes AAF agents as HTTP endpoints, allowing remote execution
of agent tasks with configurable services and security settings.
"""

import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from aaf.framework import AgenticFrameworkX
from aaf.services import MCPToolService, A2AClientService
from aaf.abstracts import AbstractService
from aaf.state import InMemoryStateManager
from aaf.registry import AgentRegistry
from aaf.retry import RetryPolicy, RetryMiddleware


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

state_manager = InMemoryStateManager(logger)
agent_registry = AgentRegistry(logger)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI application."""
    logger.info("AAF FastAPI Service starting up...")
    yield
    logger.info("AAF FastAPI Service shutting down...")
    agent_registry.shutdown_all()
    state_manager.clear_all()


app = FastAPI(
    title="Agentic Application Framework (AAF) API",
    description="REST API for creating and executing agentic workflows with middleware support",
    version="1.0.0",
    lifespan=lifespan
)


class ServiceConfig(BaseModel):
    """Configuration for a service."""
    service_type: str = Field(..., description="Type of service: 'mcp_tool' or 'a2a_client'")
    name: str = Field(..., description="Service name (e.g., 'search', 'assistant_agent')")
    require_auth: bool = Field(default=True, description="Whether this service requires authentication")


class AgentExecutionRequest(BaseModel):
    """Request model for agent execution."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    framework: str = Field(default="langgraph", description="Workflow framework to use")
    services: List[ServiceConfig] = Field(..., description="List of services the agent can use")
    security: bool = Field(default=True, description="Whether to enable AuthMiddleware")
    context: Dict[str, Any] = Field(default_factory=dict, description="Agent execution context")
    token_map: Dict[str, str] = Field(default_factory=dict, description="Service name to token mapping")
    request: Dict[str, Any] = Field(..., description="Request payload for the agent")


class AgentExecutionResponse(BaseModel):
    """Response model for agent execution."""
    agent_id: str
    status: str
    response: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    framework: str


def create_services(service_configs: List[ServiceConfig]) -> List[AbstractService]:
    """
    Create service instances from configurations.
    
    Args:
        service_configs: List of service configurations
        
    Returns:
        List of initialized service instances
        
    Raises:
        HTTPException: If service type is not supported
    """
    services = []
    
    for config in service_configs:
        if config.service_type == "mcp_tool":
            service = MCPToolService(
                tool_name=config.name,
                require_auth=config.require_auth
            )
            services.append(service)
        elif config.service_type == "a2a_client":
            service = A2AClientService(target_agent=config.name)
            services.append(service)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported service type: {config.service_type}. "
                       f"Supported types: 'mcp_tool', 'a2a_client'"
            )
    
    return services


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        framework="AAF (Agentic Application Framework)"
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        framework="AAF (Agentic Application Framework)"
    )


@app.post("/agent/execute", response_model=AgentExecutionResponse)
async def execute_agent(request: AgentExecutionRequest):
    """
    Execute an agent with the specified configuration and services.
    
    Args:
        request: Agent execution request containing configuration and payload
        
    Returns:
        Agent execution response with results or error
    """
    logger.info(f"Executing agent: {request.agent_id}")
    logger.info(f"Framework: {request.framework}, Security: {request.security}")
    logger.info(f"Services: {[s.service_type + ':' + s.name for s in request.services]}")
    
    try:
        framework = AgenticFrameworkX(logger)
        
        services = create_services(request.services)
        
        agent = framework.create_agent(
            agent_id=request.agent_id,
            framework=request.framework,
            services=services,
            security=request.security,
            config={"api_request": True}
        )
        
        input_data = {
            "context": request.context,
            "token_map": request.token_map,
            "request": request.request
        }
        
        result = agent.execute(input_data)
        
        agent.shutdown()
        
        return AgentExecutionResponse(
            agent_id=result.get('agent_id', request.agent_id),
            status="success",
            response=result.get('response'),
            metadata=result.get('metadata', {})
        )
        
    except PermissionError as e:
        logger.error(f"Permission error executing agent {request.agent_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error executing agent {request.agent_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )


@app.post("/demo/scenario1", response_model=AgentExecutionResponse)
async def demo_scenario_1():
    """
    Execute Demo Scenario 1: Secure MCP Tool with authentication.
    
    This scenario demonstrates successful agent execution with security enabled.
    """
    request = AgentExecutionRequest(
        agent_id="demo_secure_agent",
        framework="langgraph",
        services=[
            ServiceConfig(
                service_type="mcp_tool",
                name="search",
                require_auth=True
            )
        ],
        security=True,
        context={"user": "api_demo", "session": "demo_session_1"},
        token_map={
            "mcp_tool_search": "demo_secure_token_123"
        },
        request={
            "params": {
                "query": "What is the weather today?",
                "max_results": 5
            }
        }
    )
    
    return await execute_agent(request)


@app.post("/demo/scenario2", response_model=AgentExecutionResponse)
async def demo_scenario_2():
    """
    Execute Demo Scenario 2: A2A Delegation without security (should fail).
    
    This scenario demonstrates PermissionError when security is disabled
    and a service requires authentication.
    """
    request = AgentExecutionRequest(
        agent_id="demo_insecure_agent",
        framework="langgraph",
        services=[
            ServiceConfig(
                service_type="a2a_client",
                name="assistant_agent",
                require_auth=True
            )
        ],
        security=False,
        context={"user": "api_demo", "session": "demo_session_2"},
        token_map={
            "a2a_client_assistant_agent": "demo_a2a_token_456"
        },
        request={
            "task": {
                "action": "summarize",
                "data": "Summarize this document"
            }
        }
    )
    
    return await execute_agent(request)


@app.get("/state/agents", response_model=List[str])
async def list_agent_states():
    """
    List all agents with stored state.
    
    Returns:
        List of agent IDs with stored state
    """
    return state_manager.list_agents()


@app.post("/state/{agent_id}")
async def save_agent_state(agent_id: str, state: Dict[str, Any]):
    """
    Save agent state.
    
    Args:
        agent_id: Agent identifier
        state: State data to save
        
    Returns:
        Success status
    """
    success = state_manager.save_state(agent_id, state)
    if success:
        return {"status": "success", "agent_id": agent_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save state"
        )


@app.get("/state/{agent_id}")
async def get_agent_state(agent_id: str):
    """
    Load agent state.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Stored state data
    """
    state = state_manager.load_state(agent_id)
    if state is not None:
        return {"agent_id": agent_id, "state": state}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No state found for agent '{agent_id}'"
        )


@app.delete("/state/{agent_id}")
async def delete_agent_state(agent_id: str):
    """
    Delete agent state.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Success status
    """
    success = state_manager.delete_state(agent_id)
    if success:
        return {"status": "deleted", "agent_id": agent_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No state found for agent '{agent_id}'"
        )


@app.get("/registry/agents", response_model=List[str])
async def list_registered_agents():
    """
    List all registered agents.
    
    Returns:
        List of registered agent IDs
    """
    return agent_registry.list_agents()


@app.get("/registry/{agent_id}")
async def get_agent_info(agent_id: str):
    """
    Get information about a registered agent.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Agent information
    """
    info = agent_registry.get_info(agent_id)
    if info:
        return info
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found in registry"
        )


@app.get("/registry")
async def get_all_agents_info():
    """
    Get information about all registered agents.
    
    Returns:
        Dictionary of agent information
    """
    return agent_registry.get_all_info()


@app.delete("/registry/{agent_id}")
async def unregister_agent(agent_id: str, shutdown: bool = True):
    """
    Unregister an agent from the registry.
    
    Args:
        agent_id: Agent identifier
        shutdown: Whether to shutdown the agent
        
    Returns:
        Success status
    """
    success = agent_registry.unregister(agent_id, shutdown=shutdown)
    if success:
        return {"status": "unregistered", "agent_id": agent_id}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' not found in registry"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=5000,
        log_level="info",
        reload=True
    )
