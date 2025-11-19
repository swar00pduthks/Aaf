"""
AG-UI Protocol Adapter for AAF

This adapter makes AAF workflows compatible with CopilotKit's AG-UI protocol,
enabling beautiful React UIs with customizable themes.

AG-UI (Agent-User Interaction) is the standard protocol for connecting
agents to frontend applications.
"""

from typing import Dict, Any, Optional, List, AsyncGenerator
from pydantic import BaseModel
import json
import logging

logger = logging.getLogger(__name__)


class AGUIMessage(BaseModel):
    """AG-UI protocol message."""
    role: str  # "user" | "assistant" | "system"
    content: str
    metadata: Optional[Dict[str, Any]] = None


class AGUIStatePatch(BaseModel):
    """AG-UI state patch event."""
    op: str  # "set" | "merge" | "delete"
    path: str
    value: Any


class AGUIToolCall(BaseModel):
    """AG-UI tool call event."""
    tool_name: str
    arguments: Dict[str, Any]
    requires_approval: bool = False


class AAFAGUIAdapter:
    """
    Adapter to expose AAF workflows via AG-UI protocol.
    
    NOTE: This is a basic implementation that runs workflows synchronously.
    For production use with real-time streaming, workflows need callback hooks
    to emit events as nodes execute. This is planned for a future release.
    
    Current behavior: Runs workflow to completion, then emits all events.
    Future: Stream events in real-time as workflow executes.
    
    This makes AAF compatible with CopilotKit's React components:
    - <CopilotChat /> - Full chat interface
    - <CopilotSidebar /> - Sidebar chat
    - <CopilotPopup /> - Floating chat widget
    - useCoAgent() - Shared state sync
    - useCoAgentStateRender() - Generative UI
    - useCopilotAction() - Human-in-the-loop
    
    Example:
        adapter = AAFAGUIAdapter(workflow=chat_workflow)
        
        # Stream AG-UI events
        async for event in adapter.stream_events(user_query="Show me users"):
            # Send to frontend via SSE/WebSocket
            yield event
    """
    
    def __init__(self, workflow, agent_name: str = "aaf_agent"):
        """
        Initialize AG-UI adapter.
        
        Args:
            workflow: AAF workflow function (decorated with @workflow_graph)
            agent_name: Name of the agent (shown in UI)
        """
        self.workflow = workflow
        self.agent_name = agent_name
        self.state = {}
    
    async def stream_events(
        self,
        user_query: str,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream AG-UI events as workflow executes.
        
        Args:
            user_query: User's natural language query
            initial_state: Optional initial workflow state
            
        Yields:
            AG-UI protocol events (JSON-serializable dicts)
        """
        logger.info(f"[AGUI] Starting workflow for query: {user_query}")
        
        # Send initial message
        yield self._create_message("assistant", f"Processing: {user_query}")
        
        try:
            # Execute AAF workflow
            result = self.workflow(user_query)
            
            # Extract visited nodes for progress tracking
            visited_nodes = result.get("_visited_nodes", [])
            
            # Send state patches for each node
            for i, node_id in enumerate(visited_nodes):
                yield self._create_state_patch(
                    "merge",
                    "/progress",
                    {
                        "current_node": node_id,
                        "total_nodes": len(visited_nodes),
                        "percentage": int((i + 1) / len(visited_nodes) * 100)
                    }
                )
            
            # Send final result
            response = result.get("response", {})
            yield self._create_message(
                "assistant",
                self._format_response(response)
            )
            
            # Send final state
            yield self._create_state_patch("set", "/result", response)
            
            logger.info("[AGUI] Workflow completed successfully")
            
        except Exception as e:
            logger.error(f"[AGUI] Workflow failed: {e}")
            yield self._create_message(
                "assistant",
                f"Error: {str(e)}",
                metadata={"error": True}
            )
    
    def _create_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create AG-UI message event."""
        return {
            "type": "message",
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
    
    def _create_state_patch(
        self,
        op: str,
        path: str,
        value: Any
    ) -> Dict[str, Any]:
        """Create AG-UI state patch event."""
        return {
            "type": "state_patch",
            "op": op,
            "path": path,
            "value": value
        }
    
    def _create_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        requires_approval: bool = False
    ) -> Dict[str, Any]:
        """Create AG-UI tool call event."""
        return {
            "type": "tool_call",
            "tool_name": tool_name,
            "arguments": arguments,
            "requires_approval": requires_approval
        }
    
    def _format_response(self, response: Dict[str, Any]) -> str:
        """Format workflow response for display."""
        response_type = response.get("type", "unknown")
        
        if response_type == "sql":
            return f"```sql\n{response.get('query', '')}\n```"
        elif response_type == "search":
            return f"Search completed: {response.get('message', '')}"
        elif response_type == "research":
            tools_used = response.get("tools_used", [])
            return f"Research complete! Used tools: {', '.join(tools_used)}"
        else:
            return response.get("message", "Task completed")


def create_agui_fastapi_endpoint(workflow, agent_name: str = "aaf_agent"):
    """
    Create a FastAPI endpoint that serves AG-UI events.
    
    This endpoint is compatible with CopilotKit's runtime.
    
    Example:
        from fastapi import FastAPI
        from fastapi.responses import StreamingResponse
        
        app = FastAPI()
        
        @app.post("/api/copilotkit")
        async def copilotkit_endpoint(request: dict):
            adapter = AAFAGUIAdapter(workflow=chat_workflow)
            
            async def event_stream():
                async for event in adapter.stream_events(request["message"]):
                    yield f"data: {json.dumps(event)}\n\n"
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream"
            )
    """
    from fastapi.responses import StreamingResponse
    
    async def endpoint(request: Dict[str, Any]):
        adapter = AAFAGUIAdapter(workflow=workflow, agent_name=agent_name)
        
        async def event_stream():
            user_query = request.get("message", "")
            async for event in adapter.stream_events(user_query):
                # Server-Sent Events format
                yield f"data: {json.dumps(event)}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    return endpoint
