"""
FastAPI Server for Personal Finance Agent

Run this to expose the finance agent via HTTP endpoints:
  python examples/personal_finance_agent/finance_api.py

Endpoints:
  POST /finance/chat - Chat with finance agent
  POST /api/copilotkit - CopilotKit integration
  GET /finance/summary - Get financial summary
  GET /finance/transactions - List transactions
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import logging

from examples.personal_finance_agent.finance_agent import personal_finance_agent
from aaf.agui_adapter import AAFAGUIAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personal Finance Assistant API",
    description="AI-powered financial assistant using AAF framework",
    version="1.0.0"
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request for finance chat."""
    message: str = Field(..., description="User's message about finances")


class ChatResponse(BaseModel):
    """Response from finance agent."""
    message: str
    intent: str
    data: Optional[Dict[str, Any]] = None


class CopilotKitRequest(BaseModel):
    """CopilotKit request."""
    message: str
    threadId: Optional[str] = None
    agentName: Optional[str] = "finance_assistant"


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "Personal Finance Assistant",
        "framework": "AAF (Agentic Application Framework)",
        "features": [
            "Expense tracking (MCP tools)",
            "Income tracking (MCP tools)",
            "Spending analysis (Autonomous agent)",
            "Budget recommendations (Autonomous agent)",
            "Investment advice (A2A delegation)"
        ],
        "endpoints": {
            "/finance/chat": "Chat with finance agent",
            "/api/copilotkit": "CopilotKit integration (SSE)",
            "/docs": "Interactive API documentation"
        }
    }


@app.post("/finance/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the personal finance agent.
    
    Examples:
      - "I spent $50 on groceries"
      - "Show me my spending summary"
      - "How can I save more money?"
      - "What should I invest in?"
    """
    logger.info(f"Finance chat: {request.message}")
    
    try:
        # Execute workflow
        result = personal_finance_agent(request.message)
        
        return ChatResponse(
            message=result["response"]["message"],
            intent=result.get("intent", "unknown"),
            data=result["response"].get("data")
        )
        
    except Exception as e:
        logger.error(f"Finance agent error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/copilotkit")
async def copilotkit_endpoint(request: CopilotKitRequest):
    """
    CopilotKit integration endpoint.
    
    Use in React:
      <CopilotKit runtimeUrl="/api/copilotkit" agent="finance_assistant">
        <YourApp />
        <CopilotSidebar 
          labels={{
            title: "Finance Assistant",
            initial: "Track expenses, get budget advice, investment tips!"
          }}
        />
      </CopilotKit>
    """
    logger.info(f"[CopilotKit] Finance request: {request.message}")
    
    # Create AG-UI adapter
    adapter = AAFAGUIAdapter(
        workflow=personal_finance_agent,
        agent_name="finance_assistant"
    )
    
    async def event_stream():
        """Stream AG-UI events."""
        try:
            async for event in adapter.stream_events(request.message):
                yield f"data: {json.dumps(event)}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.error(f"[CopilotKit] Error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )


@app.get("/finance/summary")
async def get_summary():
    """Get financial summary (quick endpoint)."""
    result = personal_finance_agent("Show me my spending summary")
    return result["response"]


@app.get("/finance/demo")
async def demo():
    """Demo the finance agent capabilities."""
    examples = [
        {
            "query": "I spent $45.99 at Whole Foods",
            "intent": "track_expense",
            "description": "Track expense using MCP tool"
        },
        {
            "query": "My salary was $5000 this month",
            "intent": "track_income",
            "description": "Track income using MCP tool"
        },
        {
            "query": "Show me my spending summary",
            "intent": "view_summary",
            "description": "Autonomous agent analyzes spending"
        },
        {
            "query": "How can I save more money?",
            "intent": "get_budget_advice",
            "description": "Autonomous agent with budget analysis tools"
        },
        {
            "query": "What should I invest in?",
            "intent": "invest_advice",
            "description": "A2A delegation to investment specialist"
        }
    ]
    
    return {
        "agent": "Personal Finance Assistant",
        "capabilities": [
            "MCP tool integration (transaction tracking)",
            "A2A protocol (investment advisor delegation)",
            "Autonomous agents (analysis, recommendations)",
            "Workflow orchestration (conditional routing)"
        ],
        "examples": examples,
        "try_it": "POST /finance/chat with any example query"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
