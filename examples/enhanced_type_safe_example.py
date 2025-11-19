"""
Example: Type-safe agent with Pydantic AI-like features.

This demonstrates AAF's enhanced capabilities that match Pydantic AI:
- Full type safety with Pydantic models
- Generic result types
- Tool registration
- Multi-provider support
- Streaming (async)
"""

from pydantic import BaseModel, Field
from aaf.enhanced_agent import EnhancedAgent
from aaf.models import LLMMessage
from typing import List
import asyncio
import logging

logging.basicConfig(level=logging.INFO)


# Define type-safe output models
class ResearchOutput(BaseModel):
    """Type-safe research output."""
    summary: str = Field(description="Brief summary of findings")
    key_findings: List[str] = Field(description="List of key findings")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    sources: List[str] = Field(default_factory=list, description="Source references")


class SupportTicketOutput(BaseModel):
    """Type-safe support ticket analysis."""
    severity: str = Field(description="low, medium, high, critical")
    category: str = Field(description="bug, feature_request, question, etc.")
    suggested_action: str = Field(description="Recommended action")
    escalate: bool = Field(description="Whether to escalate to human")


def example_1_type_safe_research():
    """Example 1: Type-safe research agent with validation."""
    print("\n" + "="*60)
    print("Example 1: Type-Safe Research Agent")
    print("="*60)
    
    # Create agent with type-safe output
    agent = EnhancedAgent(
        agent_id="researcher",
        model="openai:gpt-4",
        result_type=ResearchOutput,
        instructions="You are a research assistant. Provide accurate, cited information."
    )
    
    # Register tools
    @agent.tool
    def search_papers(query: str, limit: int = 5) -> List[str]:
        """Search for academic papers."""
        print(f"  🔍 Searching papers for: {query}")
        return [
            "Paper 1: Quantum Computing Applications",
            "Paper 2: Machine Learning in Physics",
            "Paper 3: Neural Network Architectures"
        ][:limit]
    
    @agent.tool
    def get_citations(paper_title: str) -> str:
        """Get citation for a paper."""
        return f"Citation for '{paper_title}' (2024)"
    
    # Run the agent
    print("\n📝 Running research agent...")
    result = agent.run_sync("Research recent advances in quantum computing")
    
    print(f"\n✅ Status: {result.status}")
    print(f"📊 Result: {result.result}")
    print(f"⏱️  Execution time: {result.metadata.execution_time:.2f}s")
    print(f"🔧 Framework: {result.metadata.framework}")


def example_2_multi_provider():
    """Example 2: Multi-provider support (switch models easily)."""
    print("\n" + "="*60)
    print("Example 2: Multi-Provider Support")
    print("="*60)
    
    models = [
        "openai:gpt-4",
        "anthropic:claude-3-5-sonnet",
        "gemini:gemini-2.0-flash"
    ]
    
    for model in models:
        print(f"\n🤖 Testing {model}...")
        
        agent = EnhancedAgent(
            agent_id="tester",
            model=model,
            instructions="You are a helpful assistant."
        )
        
        result = agent.run_sync("Say hello in one sentence")
        print(f"  Response: {result.result}")
        print(f"  Time: {result.metadata.execution_time:.2f}s")


def example_3_support_ticket_classifier():
    """Example 3: Support ticket classification with structured output."""
    print("\n" + "="*60)
    print("Example 3: Support Ticket Classifier")
    print("="*60)
    
    agent = EnhancedAgent(
        agent_id="support_classifier",
        model="openai:gpt-4",
        result_type=SupportTicketOutput,
        instructions="Classify support tickets and recommend actions."
    )
    
    tickets = [
        "App crashes when I click the save button",
        "How do I export my data to CSV?",
        "Can you add dark mode?",
        "URGENT: Payment system is down for all users!"
    ]
    
    for i, ticket in enumerate(tickets, 1):
        print(f"\n📧 Ticket {i}: {ticket}")
        result = agent.run_sync(ticket)
        print(f"  Result: {result.result}")


async def example_4_streaming():
    """Example 4: Streaming responses."""
    print("\n" + "="*60)
    print("Example 4: Streaming Responses")
    print("="*60)
    
    agent = EnhancedAgent(
        agent_id="streamer",
        model="openai:gpt-4",
        instructions="You are a storyteller."
    )
    
    print("\n📖 Streaming story...")
    print("Story: ", end="", flush=True)
    
    async for chunk in agent.run_stream("Tell me a short story about AI"):
        print(chunk, end="", flush=True)
    
    print("\n✅ Streaming complete!")


def example_5_orchestration_with_type_safety():
    """Example 5: Combine enhanced agents with AAF orchestration."""
    print("\n" + "="*60)
    print("Example 5: Multi-Agent Orchestration with Type Safety")
    print("="*60)
    
    from aaf import SequentialPattern
    
    # Create multiple type-safe agents
    researcher = EnhancedAgent(
        agent_id="researcher",
        model="openai:gpt-4",
        result_type=ResearchOutput,
        instructions="Research the topic thoroughly"
    )
    
    analyst = EnhancedAgent(
        agent_id="analyst",
        model="anthropic:claude-3-5-sonnet",
        instructions="Analyze the research findings"
    )
    
    writer = EnhancedAgent(
        agent_id="writer",
        model="gemini:gemini-2.0-flash",
        instructions="Write a clear, concise summary"
    )
    
    # Wrap them for AAF orchestration (adapter pattern)
    class EnhancedAgentAdapter:
        """Adapter to use EnhancedAgent with AAF patterns."""
        def __init__(self, enhanced_agent):
            self._agent = enhanced_agent
        
        @property
        def agent_id(self):
            return self._agent.agent_id
        
        def execute(self, input_data):
            query = input_data.get("query", input_data.get("task", ""))
            result = self._agent.run_sync(query)
            return {"result": result.result}
        
        def initialize(self, config): pass
        def shutdown(self): pass
    
    # Create pipeline
    pipeline = SequentialPattern(
        agents=[
            EnhancedAgentAdapter(researcher),
            EnhancedAgentAdapter(analyst),
            EnhancedAgentAdapter(writer)
        ]
    )
    
    print("\n🔄 Running sequential pipeline...")
    result = pipeline.execute(
        agents=[],
        initial_state={"request": {"query": "Future of AI agents"}}
    )
    
    print(f"\n✅ Pipeline status: {result['status']}")
    print(f"📊 Execution chain: {len(result['execution_chain'])} agents")
    print(f"⏱️  Total time: {result['execution_time']:.2f}s")


if __name__ == "__main__":
    # Run examples
    example_1_type_safe_research()
    example_2_multi_provider()
    example_3_support_ticket_classifier()
    
    # Async example
    print("\n" + "="*60)
    asyncio.run(example_4_streaming())
    
    # Orchestration example
    example_5_orchestration_with_type_safety()
    
    print("\n" + "="*60)
    print("✨ All examples completed!")
    print("="*60)
