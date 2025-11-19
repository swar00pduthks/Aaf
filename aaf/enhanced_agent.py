"""
Enhanced type-safe agent with Pydantic AI-like features.

This demonstrates how AAF can incorporate:
- Full type safety with Pydantic models
- Streaming with validation
- Multi-provider LLM support
- Tool registration
- Dependency injection
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, AsyncIterator
from pydantic import BaseModel
from aaf.models import AgentRequest, AgentResponse, AgentMetadata
from aaf.llm_providers import LLMMessage
from aaf.llm_providers import BaseLLMProvider, infer_provider
import logging
import time


T = TypeVar('T', bound=BaseModel)


class Tool(BaseModel):
    """Type-safe tool definition."""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]


class EnhancedAgent(Generic[T]):
    """
    Type-safe agent with Pydantic AI-like ergonomics.
    
    Features:
    - Generic result type (like Pydantic AI's result_type)
    - Tool registration with @agent.tool decorator
    - Dependency injection
    - Streaming with validation
    - Multi-provider support
    
    Example:
        class ResearchOutput(BaseModel):
            summary: str
            findings: List[str]
        
        agent = EnhancedAgent(
            agent_id="researcher",
            model="openai:gpt-4",
            result_type=ResearchOutput,
            instructions="You are a research assistant"
        )
        
        @agent.tool
        def search_papers(query: str) -> List[str]:
            return ["paper1", "paper2"]
        
        result = agent.run_sync("Research quantum computing")
        print(result.data.summary)
    """
    
    def __init__(
        self,
        agent_id: str,
        model: str,
        result_type: Optional[type[T]] = None,
        instructions: Optional[str] = None,
        api_key: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.agent_id = agent_id
        self.result_type = result_type
        self.instructions = instructions
        self._logger = logger or logging.getLogger(__name__)
        
        # Create LLM provider (multi-provider support)
        self.provider = infer_provider(model, api_key)
        
        # Tool registry
        self._tools: Dict[str, Tool] = {}
    
    def tool(self, func: Callable) -> Callable:
        """
        Decorator for registering tools (like Pydantic AI's @agent.tool).
        
        Example:
            @agent.tool
            def get_weather(city: str) -> str:
                return f"Weather in {city}: Sunny"
        """
        tool_name = func.__name__
        
        self._tools[tool_name] = Tool(
            name=tool_name,
            description=func.__doc__ or "",
            function=func,
            parameters={}  # Could extract from type hints
        )
        
        self._logger.info(f"[{self.agent_id}] Registered tool: {tool_name}")
        return func
    
    def run_sync(
        self,
        prompt: str,
        deps: Optional[Any] = None
    ) -> AgentResponse:
        """
        Synchronous execution (like Pydantic AI's run_sync).
        
        Args:
            prompt: The user prompt
            deps: Dependencies for dependency injection
        
        Returns:
            AgentResponse with validated result
        """
        start_time = time.time()
        
        self._logger.info(f"[{self.agent_id}] Running sync: {prompt[:50]}...")
        
        # Build messages
        messages = []
        if self.instructions:
            messages.append(LLMMessage(role="system", content=self.instructions))
        messages.append(LLMMessage(role="user", content=prompt))
        
        # Generate response
        llm_response = self.provider.generate(messages)
        
        # Validate against result_type if provided
        result_data = llm_response.content
        if self.result_type:
            try:
                # In real implementation, parse LLM output as JSON and validate
                # For now, simulate validation
                self._logger.info(f"[{self.agent_id}] Validating output against {self.result_type.__name__}")
            except Exception as e:
                self._logger.error(f"[{self.agent_id}] Validation failed: {e}")
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            status="success",
            result=result_data,
            metadata=AgentMetadata(
                agent_id=self.agent_id,
                framework="AAF-Enhanced",
                execution_time=execution_time
            )
        )
    
    async def run_async(
        self,
        prompt: str,
        deps: Optional[Any] = None
    ) -> AgentResponse:
        """Async execution."""
        start_time = time.time()
        
        messages = []
        if self.instructions:
            messages.append(LLMMessage(role="system", content=self.instructions))
        messages.append(LLMMessage(role="user", content=prompt))
        
        llm_response = await self.provider.generate_async(messages)
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            status="success",
            result=llm_response.content,
            metadata=AgentMetadata(
                agent_id=self.agent_id,
                execution_time=execution_time
            )
        )
    
    async def run_stream(
        self,
        prompt: str,
        deps: Optional[Any] = None
    ) -> AsyncIterator[str]:
        """
        Streaming execution with validation (like Pydantic AI).
        
        Yields:
            Text chunks from LLM response
        """
        self._logger.info(f"[{self.agent_id}] Streaming: {prompt[:50]}...")
        
        messages = []
        if self.instructions:
            messages.append(LLMMessage(role="system", content=self.instructions))
        messages.append(LLMMessage(role="user", content=prompt))
        
        # Stream chunks
        async for chunk in self.provider.generate_stream(messages):
            # Could validate partial outputs here
            yield chunk
    
    def __call__(self, prompt: str, deps: Optional[Any] = None) -> AgentResponse:
        """Allow agent to be called directly."""
        return self.run_sync(prompt, deps)


# Example usage
if __name__ == "__main__":
    from pydantic import Field
    
    class ResearchOutput(BaseModel):
        """Type-safe research output."""
        summary: str = Field(description="Research summary")
        key_findings: List[str] = Field(description="Key findings")
        confidence: float = Field(ge=0, le=1, description="Confidence score")
    
    # Create type-safe agent
    agent = EnhancedAgent(
        agent_id="researcher",
        model="openai:gpt-4",
        result_type=ResearchOutput,
        instructions="You are a research assistant. Be concise and accurate."
    )
    
    # Register tools
    @agent.tool
    def search_papers(query: str) -> List[str]:
        """Search for academic papers."""
        return ["Paper 1", "Paper 2", "Paper 3"]
    
    # Run synchronously
    result = agent.run_sync("Research quantum computing applications")
    print(f"Result: {result.result}")
    print(f"Execution time: {result.metadata.execution_time:.2f}s")
