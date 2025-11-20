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

# Old framework imports removed - now using decorator-based approach
# from aaf.framework import AgenticFrameworkX
from aaf.services import MCPToolService, A2AClientService
from aaf.abstracts import AbstractService
from examples.chat_client_workflow import chat_workflow
from aaf.state import InMemoryStateManager
from aaf.registry import AgentRegistry
from aaf.retry import RetryPolicy, RetryMiddleware
from aaf.agui_adapter import AAFAGUIAdapter
from fastapi.responses import StreamingResponse
import json


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


class ChatRequest(BaseModel):
    """Request for chat workflow."""
    user_query: str = Field(..., description="User's natural language query")


class ChatResponse(BaseModel):
    """Response from chat workflow."""
    response: Dict[str, Any]
    visited_nodes: List[str]
    final_node: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Execute the chat workflow with conditional routing.
    
    This endpoint demonstrates AAF's decorator-based workflow system with:
    - Node-based orchestration
    - Conditional routing (database/tool/research)
    - State management
    
    Example:
        POST /chat {"user_query": "Show me users"}
        → Routes to SQL generation
        
        POST /chat {"user_query": "Search for AI news"}
        → Routes to MCP tool
        
        POST /chat {"user_query": "Research quantum computing"}
        → Routes to autonomous agent
    """
    logger.info(f"Chat request: {request.user_query}")
    
    try:
        # Execute workflow (decorator-based)
        result = chat_workflow(request.user_query)
        
        return ChatResponse(
            response=result.get("response", {}),
            visited_nodes=result.get("_visited_nodes", []),
            final_node=result.get("_final_node", "unknown")
        )
        
    except Exception as e:
        logger.error(f"Chat workflow error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow failed: {str(e)}"
        )


# OLD ENDPOINT - Using deprecated protocol-based approach
# Commented out for reference, will be removed in future version

# ============================================================================
# Demo endpoint
# ============================================================================

@app.get("/demo")
async def demo():
    """Demo endpoint showing AAF capabilities."""
    return {
        "message": "AAF - Agentic Application Framework",
        "approach": "Decorator-based node orchestration",
        "endpoints": {
            "/chat": "Chat workflow with conditional routing",
            "/api/copilotkit": "CopilotKit integration endpoint (SSE)",
            "/docs": "Interactive API documentation",
            "/health": "Health check"
        },
        "example": {
            "endpoint": "/chat",
            "method": "POST",
            "body": {"user_query": "Show me users"}
        }
    }


# ============================================================================
# CopilotKit Integration Endpoint
# ============================================================================

class CopilotKitRequest(BaseModel):
    """Request model for CopilotKit integration."""
    message: str = Field(..., description="User's message to the agent")
    threadId: Optional[str] = Field(None, description="Thread ID for conversation context")
    agentName: Optional[str] = Field("aaf_agent", description="Name of the agent to use")


@app.post("/api/copilotkit")
async def copilotkit_endpoint(request: CopilotKitRequest):
    """
    CopilotKit AG-UI Protocol endpoint.
    
    This endpoint allows AAF workflows to be embedded in React applications
    using CopilotKit's beautiful UI components.
    
    Compatible with:
    - <CopilotChat /> - Full chat interface
    - <CopilotSidebar /> - Sidebar chat
    - <CopilotPopup /> - Floating chat widget
    
    Usage in React:
        ```tsx
        import { CopilotKit } from '@copilotkit/react-core';
        import { CopilotSidebar } from '@copilotkit/react-ui';
        
        <CopilotKit runtimeUrl="/api/copilotkit" agent="aaf_agent">
          <YourApp />
          <CopilotSidebar defaultOpen={true} />
        </CopilotKit>
        ```
    
    Example request:
        POST /api/copilotkit
        {
            "message": "Show me all users",
            "threadId": "thread-123",
            "agentName": "aaf_agent"
        }
    
    Response: Server-Sent Events (SSE) stream with AG-UI protocol messages
    """
    logger.info(f"[CopilotKit] Received request: {request.message}")
    
    # Create AG-UI adapter with the chat workflow
    adapter = AAFAGUIAdapter(
        workflow=chat_workflow,
        agent_name=request.agentName or "aaf_agent"
    )
    
    async def event_stream():
        """Stream AG-UI events as Server-Sent Events."""
        try:
            async for event in adapter.stream_events(request.message):
                # SSE format: data: {json}\n\n
                yield f"data: {json.dumps(event)}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error(f"[CopilotKit] Stream error: {e}")
            error_event = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
