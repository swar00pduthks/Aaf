"""
Pydantic AI + AAF Integration - Best of Both Worlds!

This shows how AAF uses Pydantic AI as the base implementation
while adding decorator simplicity and orchestration.
"""

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Check if pydantic-ai is available
try:
    from pydantic import BaseModel, Field
    from aaf.pydantic_decorators import pydantic_agent, chatbot, from_pydantic_ai
    from aaf import workflow, validate, retry, with_memory
    
    PYDANTIC_AI_AVAILABLE = True
except ImportError as e:
    PYDANTIC_AI_AVAILABLE = False
    print(f"⚠️  Pydantic AI not installed: {e}")
    print("   Install with: pip install pydantic-ai")


if PYDANTIC_AI_AVAILABLE:
    
    # =================================================================
    # Example 1: Type-Safe Agent with Pydantic AI
    # =================================================================
    
    class ResearchOutput(BaseModel):
        """Type-safe research output."""
        summary: str = Field(description="Brief summary")
        key_findings: list[str] = Field(description="Key findings")
        confidence: float = Field(ge=0, le=1, description="Confidence 0-1")
    
    
    @pydantic_agent(
        model="openai:gpt-4",
        result_type=ResearchOutput,
        instructions="You are a research assistant. Be thorough and cite sources."
    )
    def type_safe_researcher(query: str):
        """
        Type-safe research agent powered by Pydantic AI.
        Output is automatically validated!
        """
        return query  # Pydantic AI handles the LLM call
    
    
    # =================================================================
    # Example 2: Simple Chatbot
    # =================================================================
    
    @chatbot(model="anthropic:claude-3-5-sonnet")
    def support_chatbot():
        """You are a friendly customer support agent."""
        pass
    
    
    # =================================================================
    # Example 3: Add AAF Features to Pydantic AI Agent
    # =================================================================
    
    @retry(max_attempts=3)
    @validate(lambda r: r is not None)
    @pydantic_agent(model="openai:gpt-4")
    def robust_agent(query: str):
        """Pydantic AI agent with AAF retry + validation."""
        return query
    
    
    # =================================================================
    # Example 4: Multi-Agent Workflow (Pydantic AI + AAF Orchestration)
    # =================================================================
    
    @pydantic_agent(
        model="openai:gpt-4",
        result_type=ResearchOutput,
        agent_id="researcher"
    )
    def researcher(query: str):
        """Research agent."""
        return query
    
    
    @pydantic_agent(
        model="anthropic:claude-3-5-sonnet",
        agent_id="analyzer"
    )
    def analyzer(research: str):
        """Analysis agent."""
        return research
    
    
    @pydantic_agent(
        model="gemini:gemini-2.0-flash",
        agent_id="writer"
    )
    def writer(analysis: str):
        """Writing agent."""
        return analysis
    
    
    # Orchestrate Pydantic AI agents with AAF!
    @workflow(researcher, analyzer, writer, pattern="sequential")
    def research_pipeline(query: str):
        """
        Multi-provider pipeline:
        - OpenAI for research
        - Anthropic for analysis  
        - Gemini for writing
        
        All type-safe, all orchestrated by AAF!
        """
        pass
    
    
    # =================================================================
    # Example 5: Wrap Existing Pydantic AI Agent
    # =================================================================
    
    def example_existing_pydantic_ai_agent():
        """Show how to wrap existing Pydantic AI agents."""
        from pydantic_ai import Agent as PydanticAgent
        
        # Your existing Pydantic AI agent
        existing_agent = PydanticAgent(
            'openai:gpt-4',
            result_type=ResearchOutput,
            system_prompt="You are a research assistant"
        )
        
        # Wrap it for AAF
        aaf_wrapped = from_pydantic_ai(existing_agent, "existing_agent")
        
        # Now use with AAF orchestration
        @workflow(aaf_wrapped, analyzer, pattern="sequential")
        def hybrid_pipeline(query):
            pass
        
        return hybrid_pipeline
    
    
    # =================================================================
    # Run Examples
    # =================================================================
    
    def run_examples():
        print("="*60)
        print("Pydantic AI + AAF Integration Examples")
        print("="*60)
        
        # Note: These are simulations since we don't have API keys
        print("\n1️⃣ Type-Safe Agent (Pydantic AI base):")
        print("   ✅ Full type safety with Pydantic models")
        print("   ✅ Multi-provider support (20+ LLMs)")
        print("   ✅ Automatic validation")
        
        print("\n2️⃣ Chatbot (Pydantic AI base):")
        print("   ✅ Conversation history")
        print("   ✅ Context awareness")
        
        print("\n3️⃣ AAF Features on Top:")
        print("   ✅ @retry for fault tolerance")
        print("   ✅ @validate for safety")
        print("   ✅ @with_memory for context")
        
        print("\n4️⃣ Multi-Agent Orchestration:")
        print("   ✅ OpenAI + Anthropic + Gemini in one pipeline")
        print("   ✅ Type-safe throughout")
        print("   ✅ AAF orchestration")
        
        print("\n" + "="*60)
        print("✨ Best of Both Worlds!")
        print("="*60)
        print("\n📊 What You Get:")
        print("   FROM Pydantic AI:")
        print("     • Type safety & validation")
        print("     • 20+ LLM providers")
        print("     • Streaming support")
        print("     • Tool registration")
        print("     • Dependency injection")
        print("\n   FROM AAF:")
        print("     • Decorator simplicity (@agent, @workflow)")
        print("     • Multi-framework orchestration")
        print("     • Production features (memory, HITL, guardrails)")
        print("     • REST API layer")
        print("\n   = PERFECT COMBINATION! 🎯")
    
    
    if __name__ == "__main__":
        run_examples()

else:
    print("\n" + "="*60)
    print("Install Pydantic AI to see these examples:")
    print("  pip install pydantic-ai")
    print("="*60)
