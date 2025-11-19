"""
Example: Using AAF's llm_providers.py for multi-provider LLM calls

This shows how to use AAF's own LLM provider abstraction
(alternative to Pydantic AI)
"""

from aaf.llm_providers import (
    infer_provider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    LLMMessage
)
from aaf import EnhancedAgent
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


# =============================================================================
# Example 1: Direct Provider Usage
# =============================================================================

def example_1_direct_provider():
    """Use providers directly for LLM calls."""
    print("\n" + "="*60)
    print("Example 1: Direct Provider Usage")
    print("="*60)
    
    # Create providers using auto-detection
    openai = infer_provider("openai:gpt-4")
    claude = infer_provider("anthropic:claude-3-5-sonnet")
    gemini = infer_provider("gemini:gemini-2.0-flash")
    
    # Or create them directly
    # openai = OpenAIProvider(model_name="gpt-4", api_key="your-key")
    
    # Prepare messages
    messages = [
        LLMMessage(role="system", content="You are a helpful assistant"),
        LLMMessage(role="user", content="What is quantum computing?")
    ]
    
    # Call different providers with same interface
    print("\n📞 Calling OpenAI...")
    response_openai = openai.generate(messages)
    print(f"   {response_openai.content}")
    print(f"   Model: {response_openai.model}")
    
    print("\n📞 Calling Anthropic...")
    response_claude = claude.generate(messages)
    print(f"   {response_claude.content}")
    
    print("\n📞 Calling Gemini...")
    response_gemini = gemini.generate(messages)
    print(f"   {response_gemini.content}")
    
    print("\n✅ All providers use the same interface!")


# =============================================================================
# Example 2: Streaming Responses
# =============================================================================

async def example_2_streaming():
    """Stream responses from LLMs."""
    print("\n" + "="*60)
    print("Example 2: Streaming Responses")
    print("="*60)
    
    provider = infer_provider("openai:gpt-4")
    
    messages = [
        LLMMessage(role="user", content="Tell me a story")
    ]
    
    print("\n📡 Streaming from OpenAI...")
    print("   ", end="")
    async for chunk in provider.generate_stream(messages):
        print(chunk, end="", flush=True)
    print("\n\n✅ Streaming complete!")


# =============================================================================
# Example 3: Using with EnhancedAgent
# =============================================================================

def example_3_enhanced_agent():
    """Use llm_providers.py through EnhancedAgent."""
    print("\n" + "="*60)
    print("Example 3: EnhancedAgent with LLM Providers")
    print("="*60)
    
    # Define type-safe output
    class ResearchOutput(BaseModel):
        summary: str
        key_points: list[str]
        confidence: float
    
    # EnhancedAgent uses llm_providers.py internally
    agent = EnhancedAgent(
        agent_id="researcher",
        model="openai:gpt-4",  # Automatically uses OpenAIProvider
        result_type=ResearchOutput,
        instructions="You are a research assistant"
    )
    
    print("\n🤖 Agent created with:")
    print(f"   Model: openai:gpt-4")
    print(f"   Provider: {agent.provider.__class__.__name__}")
    print(f"   Result Type: {ResearchOutput.__name__}")
    
    # Note: run_sync would call the LLM
    # result = agent.run_sync("Research quantum computing")
    # print(f"\n📊 Result: {result.data.summary}")
    
    print("\n✅ EnhancedAgent automatically uses llm_providers.py!")


# =============================================================================
# Example 4: Switching Providers Dynamically
# =============================================================================

def example_4_switch_providers():
    """Switch between providers at runtime."""
    print("\n" + "="*60)
    print("Example 4: Dynamic Provider Switching")
    print("="*60)
    
    # Same messages for all providers
    messages = [
        LLMMessage(role="user", content="Explain AI in one sentence")
    ]
    
    # List of providers to try
    provider_models = [
        "openai:gpt-4",
        "anthropic:claude-3-5-sonnet",
        "gemini:gemini-2.0-flash"
    ]
    
    print("\n🔄 Testing all providers with same query...\n")
    
    for model_string in provider_models:
        provider = infer_provider(model_string)
        response = provider.generate(messages)
        
        print(f"✓ {model_string}")
        print(f"  → {response.content}\n")
    
    print("✅ Same code works with any provider!")


# =============================================================================
# Example 5: Real-World Pattern
# =============================================================================

def example_5_real_world():
    """Real-world usage pattern."""
    print("\n" + "="*60)
    print("Example 5: Real-World Usage Pattern")
    print("="*60)
    
    class AgentWithFallback:
        """Agent that tries multiple providers if one fails."""
        
        def __init__(self):
            self.providers = [
                infer_provider("openai:gpt-4"),
                infer_provider("anthropic:claude-3-5-sonnet"),
                infer_provider("gemini:gemini-2.0-flash")
            ]
        
        def generate(self, messages):
            """Try providers in order until one succeeds."""
            for provider in self.providers:
                try:
                    return provider.generate(messages)
                except Exception as e:
                    print(f"   ⚠️  {provider.__class__.__name__} failed: {e}")
                    continue
            raise Exception("All providers failed")
    
    # Use it
    agent = AgentWithFallback()
    
    messages = [
        LLMMessage(role="user", content="Hello!")
    ]
    
    print("\n🔄 Agent with automatic fallback...\n")
    response = agent.generate(messages)
    print(f"✓ Got response: {response.content}")
    
    print("\n✅ Production-ready pattern with redundancy!")


# =============================================================================
# Run All Examples
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("AAF LLM Providers - Multi-Provider LLM Interface")
    print("="*60)
    
    example_1_direct_provider()
    
    # Async example (commented out - requires async runtime)
    # import asyncio
    # asyncio.run(example_2_streaming())
    
    example_3_enhanced_agent()
    example_4_switch_providers()
    example_5_real_world()
    
    print("\n" + "="*60)
    print("Key Takeaways:")
    print("="*60)
    print("\n1. Unified Interface:")
    print("   All providers (OpenAI, Anthropic, Gemini) use same API")
    print("\n2. Auto-Detection:")
    print("   infer_provider('openai:gpt-4') automatically creates right provider")
    print("\n3. EnhancedAgent:")
    print("   Uses llm_providers.py internally for type-safe agents")
    print("\n4. No Pydantic AI Dependency:")
    print("   This is AAF's own implementation!")
    print("\n5. Production Pattern:")
    print("   Easy to add fallbacks, retries, logging")
    print("\n" + "="*60)
    
    print("\n⚠️  NOTE: Current implementation uses MOCK responses.")
    print("    To use real LLMs, add actual API clients:")
    print("    - OpenAI: pip install openai")
    print("    - Anthropic: pip install anthropic")
    print("    - Gemini: pip install google-generativeai")
    print("="*60)
