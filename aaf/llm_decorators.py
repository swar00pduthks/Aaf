"""
LLM Provider decorators - AAF's own LLM agents (no Pydantic AI dependency)

Uses llm_providers.py to create type-safe agents with multi-provider support.
"""

from typing import Callable, Optional, Type, TypeVar
from pydantic import BaseModel
from functools import wraps
import logging

from aaf.llm_providers import infer_provider, LLMMessage
from aaf.enhanced_agent import EnhancedAgent

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def llm_agent(
    model: str = "openai:gpt-4",
    result_type: Optional[Type[T]] = None,
    instructions: Optional[str] = None,
    agent_id: Optional[str] = None,
    api_key: Optional[str] = None
):
    """
    Create an LLM-powered agent using AAF's llm_providers.py (no Pydantic AI dependency).
    
    This gives you:
    - Multi-provider support (OpenAI, Anthropic, Gemini, etc.)
    - Type-safe outputs with Pydantic models
    - Streaming support
    - Tool registration
    - NO dependency on Pydantic AI library
    
    Example:
        from pydantic import BaseModel
        
        class ResearchOutput(BaseModel):
            summary: str
            findings: list[str]
            confidence: float
        
        @llm_agent(
            model="openai:gpt-4",
            result_type=ResearchOutput,
            instructions="You are a research assistant"
        )
        def researcher(query: str):
            return query  # EnhancedAgent handles LLM call
        
        # Use it
        result = researcher("quantum computing")
        print(result.summary)  # Type-safe access!
    
    Multi-Provider Examples:
        @llm_agent(model="openai:gpt-4")
        def openai_agent(query): return query
        
        @llm_agent(model="anthropic:claude-3-5-sonnet")
        def claude_agent(query): return query
        
        @llm_agent(model="gemini:gemini-2.0-flash")
        def gemini_agent(query): return query
    """
    def decorator(func: Callable):
        # Create EnhancedAgent (uses llm_providers.py internally)
        _agent_id = agent_id or func.__name__
        _instructions = instructions or func.__doc__ or "You are a helpful assistant."
        
        enhanced_agent = EnhancedAgent(
            agent_id=_agent_id,
            model=model,
            result_type=result_type,
            instructions=_instructions,
            api_key=api_key
        )
        
        # Create wrapper that works with AAF
        class LLMAgentWrapper:
            def __init__(self):
                self._enhanced_agent = enhanced_agent
                self._func = func
                self._id = _agent_id
            
            @property
            def agent_id(self):
                return self._id
            
            @property
            def __name__(self):
                return self._id
            
            @property
            def provider(self):
                """Access the underlying LLM provider."""
                return self._enhanced_agent.provider
            
            def execute(self, input_data: dict) -> dict:
                """Execute as AAF agent."""
                query = input_data.get("query", input_data.get("task", ""))
                
                # Run EnhancedAgent
                result = self._enhanced_agent.run_sync(query)
                
                return {
                    "status": "success",
                    "result": result.data if hasattr(result, 'data') else result,
                    "agent_id": self._id,
                    "framework": "AAF-LLM",
                    "provider": self.provider.__class__.__name__
                }
            
            def run_sync(self, prompt: str, **kwargs):
                """Direct EnhancedAgent interface."""
                return self._enhanced_agent.run_sync(prompt, **kwargs)
            
            async def run_async(self, prompt: str, **kwargs):
                """Async EnhancedAgent interface."""
                return await self._enhanced_agent.run_async(prompt, **kwargs)
            
            async def run_stream(self, prompt: str, **kwargs):
                """Streaming EnhancedAgent interface."""
                async for chunk in self._enhanced_agent.run_stream(prompt, **kwargs):
                    yield chunk
            
            def tool(self, func: Callable):
                """Register tools (EnhancedAgent style)."""
                return self._enhanced_agent.tool(func)
            
            def __call__(self, *args, **kwargs):
                """Call with prompt or execute function."""
                if args and isinstance(args[0], str):
                    # Called with prompt - run LLM
                    result = self._enhanced_agent.run_sync(args[0])
                    return result.data if hasattr(result, 'data') else result
                else:
                    # Call original function
                    return self._func(*args, **kwargs)
            
            def initialize(self, config): pass
            def shutdown(self): pass
            
            def __repr__(self):
                return f"<LLMAgent '{self._id}' model={model} provider={self.provider.__class__.__name__}>"
        
        wrapper = LLMAgentWrapper()
        
        # Register with AAF
        from aaf.decorators import _AGENT_REGISTRY
        _AGENT_REGISTRY[_agent_id] = wrapper
        
        return wrapper
    
    return decorator


def multi_provider_agent(
    providers: list[str],
    result_type: Optional[Type[T]] = None,
    instructions: Optional[str] = None,
    agent_id: Optional[str] = None,
    fallback: bool = True
):
    """
    Create an agent that tries multiple LLM providers (with optional fallback).
    
    Example:
        @multi_provider_agent(
            providers=["openai:gpt-4", "anthropic:claude-3-5-sonnet", "gemini:gemini-2.0-flash"],
            fallback=True
        )
        def robust_agent(query):
            return query
        
        # Will try OpenAI first, then Claude, then Gemini if they fail
        result = robust_agent("Hello")
    """
    def decorator(func: Callable):
        _agent_id = agent_id or func.__name__
        _instructions = instructions or func.__doc__ or "You are a helpful assistant."
        
        # Create multiple EnhancedAgent instances
        agents = []
        for provider_model in providers:
            agent = EnhancedAgent(
                agent_id=f"{_agent_id}_{provider_model.replace(':', '_')}",
                model=provider_model,
                result_type=result_type,
                instructions=_instructions
            )
            agents.append((provider_model, agent))
        
        class MultiProviderWrapper:
            def __init__(self):
                self._agents = agents
                self._func = func
                self._id = _agent_id
                self._fallback = fallback
            
            @property
            def agent_id(self):
                return self._id
            
            @property
            def __name__(self):
                return self._id
            
            def execute(self, input_data: dict) -> dict:
                """Execute with fallback across providers."""
                query = input_data.get("query", input_data.get("task", ""))
                
                last_error = None
                for provider_name, agent in self._agents:
                    try:
                        logger.info(f"[MultiProvider] Trying {provider_name}...")
                        result = agent.run_sync(query)
                        
                        return {
                            "status": "success",
                            "result": result.data if hasattr(result, 'data') else result,
                            "agent_id": self._id,
                            "provider": provider_name,
                            "framework": "AAF-MultiProvider"
                        }
                    except Exception as e:
                        logger.warning(f"[MultiProvider] {provider_name} failed: {e}")
                        last_error = e
                        if not self._fallback:
                            raise
                        continue
                
                raise Exception(f"All providers failed. Last error: {last_error}")
            
            def __call__(self, prompt: str):
                """Call with automatic fallback."""
                for provider_name, agent in self._agents:
                    try:
                        result = agent.run_sync(prompt)
                        return result.data if hasattr(result, 'data') else result
                    except Exception as e:
                        if not self._fallback:
                            raise
                        continue
                raise Exception("All providers failed")
            
            def initialize(self, config): pass
            def shutdown(self): pass
            
            def __repr__(self):
                provider_list = [name for name, _ in self._agents]
                return f"<MultiProviderAgent '{self._id}' providers={provider_list}>"
        
        wrapper = MultiProviderWrapper()
        
        # Register with AAF
        from aaf.decorators import _AGENT_REGISTRY
        _AGENT_REGISTRY[_agent_id] = wrapper
        
        return wrapper
    
    return decorator
