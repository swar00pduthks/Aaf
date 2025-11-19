"""
LLM Decorators - AAF's own multi-provider LLM agents as decorators!

No Pydantic AI dependency - uses AAF's llm_providers.py
"""

from aaf import llm_agent, multi_provider_agent, workflow, retry, validate
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


# =============================================================================
# Example 1: Basic LLM Agent Decorator
# =============================================================================

@llm_agent(model="openai:gpt-4")
def simple_agent(query: str):
    """A simple LLM agent - zero boilerplate!"""
    return query


# =============================================================================
# Example 2: Type-Safe LLM Agent
# =============================================================================

class ResearchOutput(BaseModel):
    """Type-safe research output."""
    summary: str = Field(description="Brief summary")
    key_findings: list[str] = Field(description="Key findings")
    confidence: float = Field(ge=0, le=1, description="Confidence score")


@llm_agent(
    model="openai:gpt-4",
    result_type=ResearchOutput,
    instructions="You are a thorough research assistant"
)
def type_safe_researcher(query: str):
    """Type-safe research agent with validated output."""
    return query


# =============================================================================
# Example 3: Multiple Providers
# =============================================================================

@llm_agent(model="openai:gpt-4")
def openai_agent(query): return query

@llm_agent(model="anthropic:claude-3-5-sonnet")
def claude_agent(query): return query

@llm_agent(model="gemini:gemini-2.0-flash")
def gemini_agent(query): return query


# =============================================================================
# Example 4: Multi-Provider with Automatic Fallback
# =============================================================================

@multi_provider_agent(
    providers=[
        "openai:gpt-4",
        "anthropic:claude-3-5-sonnet",
        "gemini:gemini-2.0-flash"
    ],
    fallback=True
)
def robust_agent(query: str):
    """Agent that tries multiple providers if one fails."""
    return query


# =============================================================================
# Example 5: LLM Agent with AAF Feature Decorators
# =============================================================================

@retry(max_attempts=3)
@validate(lambda r: r is not None)
@llm_agent(model="openai:gpt-4")
def production_llm_agent(query: str):
    """LLM agent with retry and validation."""
    return query


# =============================================================================
# Example 6: Orchestrate Multiple LLM Providers
# =============================================================================

@workflow(openai_agent, claude_agent, gemini_agent, pattern="sequential")
def multi_provider_pipeline(query: str):
    """
    Pipeline using different providers:
    1. OpenAI analyzes
    2. Claude reviews
    3. Gemini synthesizes
    """
    pass


# =============================================================================
# Run Examples
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("AAF LLM Decorators - Multi-Provider Agents as Decorators")
    print("="*60)
    
    # Example 1: Simple agent
    print("\n1️⃣ Simple LLM Agent:")
    print(f"   Agent: {simple_agent}")
    print(f"   Provider: {simple_agent.provider.__class__.__name__}")
    
    # Example 2: Type-safe agent
    print("\n2️⃣ Type-Safe LLM Agent:")
    print(f"   Agent: {type_safe_researcher}")
    print(f"   Result Type: {ResearchOutput.__name__}")
    print(f"   Provider: {type_safe_researcher.provider.__class__.__name__}")
    
    # Example 3: Multiple providers
    print("\n3️⃣ Multiple Provider Agents:")
    print(f"   OpenAI: {openai_agent.provider.__class__.__name__}")
    print(f"   Claude: {claude_agent.provider.__class__.__name__}")
    print(f"   Gemini: {gemini_agent.provider.__class__.__name__}")
    
    # Example 4: Multi-provider with fallback
    print("\n4️⃣ Multi-Provider Agent with Fallback:")
    print(f"   Agent: {robust_agent}")
    print(f"   Providers: 3 (OpenAI, Claude, Gemini)")
    print(f"   Fallback: Enabled")
    
    # Example 5: With feature decorators
    print("\n5️⃣ LLM Agent with Feature Decorators:")
    print(f"   ✅ Retry enabled (3 attempts)")
    print(f"   ✅ Validation enabled")
    print(f"   ✅ LLM-powered (OpenAI)")
    
    # Example 6: Workflow orchestration
    print("\n6️⃣ Multi-Provider Workflow:")
    print(f"   Step 1: OpenAI (gpt-4)")
    print(f"   Step 2: Anthropic (claude-3-5-sonnet)")
    print(f"   Step 3: Gemini (gemini-2.0-flash)")
    
    print("\n" + "="*60)
    print("✨ Key Benefits:")
    print("="*60)
    print("\n1. Zero Boilerplate:")
    print("   Just @llm_agent - no classes, no manual setup")
    
    print("\n2. Multi-Provider Support:")
    print("   OpenAI, Anthropic, Gemini - same interface")
    
    print("\n3. No Pydantic AI Dependency:")
    print("   Uses AAF's own llm_providers.py")
    
    print("\n4. Type-Safe:")
    print("   Optional Pydantic result_type validation")
    
    print("\n5. Automatic Fallback:")
    print("   @multi_provider_agent tries providers in order")
    
    print("\n6. Stack with AAF Features:")
    print("   Combine with @retry, @validate, @workflow, etc.")
    
    print("\n" + "="*60)
    print("💡 Comparison:")
    print("="*60)
    
    print("\n@pydantic_agent (requires Pydantic AI):")
    print("  • Full Pydantic AI library")
    print("  • 20+ providers")
    print("  • Streaming, tools, dependency injection")
    
    print("\n@llm_agent (AAF's own):")
    print("  • No external dependency")
    print("  • Uses AAF's llm_providers.py")
    print("  • Lighter weight alternative")
    
    print("\n" + "="*60)
    print("\n⚠️  NOTE: Currently uses MOCK responses.")
    print("    To connect real LLMs, update llm_providers.py")
    print("="*60)
