"""
Pydantic AI-powered decorators - Best of both worlds!

Uses Pydantic AI as the base implementation, adds AAF's decorator simplicity.
"""

from typing import Callable, Optional, Any, TypeVar, Type
from pydantic import BaseModel
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Will be imported when pydantic-ai is installed
try:
    from pydantic_ai import Agent as PydanticAgent
    from pydantic_ai import RunContext
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    PydanticAgent = None
    RunContext = None


T = TypeVar('T', bound=BaseModel)


def pydantic_agent(
    model: str = "openai:gpt-4",
    result_type: Optional[Type[T]] = None,
    instructions: Optional[str] = None,
    agent_id: Optional[str] = None
):
    """
    Create a type-safe agent using Pydantic AI under the hood.
    
    This gives you:
    - Pydantic AI's type safety and validation
    - Multi-provider support (20+ LLMs)
    - Streaming with validation
    - Tool registration
    - Dependency injection
    
    PLUS AAF's decorator simplicity!
    
    Example:
        from pydantic import BaseModel
        
        class ResearchOutput(BaseModel):
            summary: str
            findings: list[str]
            confidence: float
        
        @pydantic_agent(
            model="openai:gpt-4",
            result_type=ResearchOutput,
            instructions="You are a research assistant"
        )
        def researcher(query: str):
            # Your custom logic here (optional)
            # Or let Pydantic AI handle it automatically
            return query
    """
    if not PYDANTIC_AI_AVAILABLE:
        raise ImportError(
            "pydantic-ai not installed. Install with: pip install pydantic-ai"
        )
    
    def decorator(func: Callable):
        # Create Pydantic AI agent
        _agent_id = agent_id or func.__name__
        _instructions = instructions or func.__doc__ or "You are a helpful assistant."
        
        pydantic_ai_agent = PydanticAgent(
            model,
            result_type=result_type,
            system_prompt=_instructions
        )
        
        # Create wrapper that works with AAF
        class PydanticAgentWrapper:
            def __init__(self):
                self._pydantic_agent = pydantic_ai_agent
                self._func = func
                self._id = _agent_id
            
            @property
            def agent_id(self):
                return self._id
            
            @property
            def __name__(self):
                return self._id
            
            def execute(self, input_data: dict) -> dict:
                """Execute as AAF agent."""
                query = input_data.get("query", input_data.get("task", ""))
                
                # Run Pydantic AI agent
                result = self._pydantic_agent.run_sync(query)
                
                return {
                    "status": "success",
                    "result": result.data if hasattr(result, 'data') else result,
                    "agent_id": self._id,
                    "framework": "PydanticAI"
                }
            
            def run_sync(self, prompt: str, **kwargs):
                """Direct Pydantic AI interface."""
                return self._pydantic_agent.run_sync(prompt, **kwargs)
            
            async def run_async(self, prompt: str, **kwargs):
                """Async Pydantic AI interface."""
                return await self._pydantic_agent.run(prompt, **kwargs)
            
            async def run_stream(self, prompt: str, **kwargs):
                """Streaming Pydantic AI interface."""
                async with self._pydantic_agent.run_stream(prompt, **kwargs) as response:
                    async for chunk in response.stream():
                        yield chunk
            
            def tool(self, func: Callable):
                """Register tools (Pydantic AI style)."""
                return self._pydantic_agent.tool(func)
            
            def __call__(self, *args, **kwargs):
                """Call the original function OR run the agent."""
                if args and isinstance(args[0], str):
                    # Called with prompt - run agent
                    result = self._pydantic_agent.run_sync(args[0])
                    return result.data if hasattr(result, 'data') else result
                else:
                    # Call original function
                    return self._func(*args, **kwargs)
            
            def initialize(self, config): pass
            def shutdown(self): pass
            
            def __repr__(self):
                return f"<PydanticAgent '{self._id}' model={model}>"
        
        wrapper = PydanticAgentWrapper()
        
        # Register with AAF
        from aaf.decorators import _AGENT_REGISTRY
        _AGENT_REGISTRY[_agent_id] = wrapper
        
        return wrapper
    
    return decorator


def chatbot(
    model: str = "openai:gpt-4",
    instructions: Optional[str] = None,
    agent_id: Optional[str] = None
):
    """
    Create a chatbot with conversation history (Pydantic AI powered).
    
    Example:
        @chatbot(model="anthropic:claude-3-5-sonnet")
        def support_bot():
            '''You are a helpful customer support agent.'''
            pass
        
        # Use it
        response1 = support_bot("Hello!")
        response2 = support_bot("What can you help with?")  # Remembers context
    """
    return pydantic_agent(
        model=model,
        result_type=None,  # String output for chatbots
        instructions=instructions,
        agent_id=agent_id
    )


# Example: Show how to use with existing Pydantic AI agents
def from_pydantic_ai(pydantic_ai_agent, agent_id: str):
    """
    Wrap an existing Pydantic AI agent for use with AAF.
    
    Example:
        from pydantic_ai import Agent as PydanticAgent
        
        # Your existing Pydantic AI agent
        my_agent = PydanticAgent('openai:gpt-4', result_type=MyOutput)
        
        # Wrap it for AAF
        aaf_agent = from_pydantic_ai(my_agent, "my_agent")
        
        # Now use with AAF orchestration
        @workflow(aaf_agent, other_agent)
        def pipeline(query): pass
    """
    if not PYDANTIC_AI_AVAILABLE:
        raise ImportError("pydantic-ai not installed")
    
    class PydanticAIAdapter:
        def __init__(self):
            self._pydantic_agent = pydantic_ai_agent
            self._id = agent_id
        
        @property
        def agent_id(self):
            return self._id
        
        @property
        def __name__(self):
            return self._id
        
        def execute(self, input_data: dict) -> dict:
            query = input_data.get("query", input_data.get("task", ""))
            result = self._pydantic_agent.run_sync(query)
            
            return {
                "status": "success",
                "result": result.data if hasattr(result, 'data') else result,
                "agent_id": self._id,
                "framework": "PydanticAI"
            }
        
        def __call__(self, prompt: str):
            result = self._pydantic_agent.run_sync(prompt)
            return result.data if hasattr(result, 'data') else result
        
        def initialize(self, config): pass
        def shutdown(self): pass
        
        def __repr__(self):
            return f"<PydanticAIAdapter '{self._id}'>"
    
    adapter = PydanticAIAdapter()
    
    # Register with AAF
    from aaf.decorators import _AGENT_REGISTRY
    _AGENT_REGISTRY[agent_id] = adapter
    
    return adapter
