"""
AAF Feature Decorators - Lambda-like simplicity for EVERYTHING!

Validators, HITL, Memory, Retry - all as simple decorators.
"""

from aaf.decorators import agent
from aaf.feature_decorators import (
    validate,
    guardrail,
    no_bulk_operations,
    requires_approval,
    human_feedback,
    with_memory,
    retry,
    plan_task,
    log_execution,
    stack
)
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


# =============================================================================
# Example 1: Validators
# =============================================================================

@validate(
    lambda result: result.get("confidence", 0) > 0.5,
    lambda result: len(result.get("text", "")) > 10
)
@agent
def validated_researcher(query: str):
    """Agent with automatic validation."""
    return {
        "text": f"Research on {query}: detailed findings here",
        "confidence": 0.85
    }


# =============================================================================
# Example 2: Guardrails
# =============================================================================

@guardrail(severity="high")
@agent
def safe_delete(count: int):
    """Agent with safety guardrails."""
    if count > 100:
        raise ValueError(f"Cannot delete {count} records - too many!")
    return f"Deleted {count} records safely"


@no_bulk_operations(max_count=50)
@agent
def limited_delete(user_ids: list):
    """Agent with bulk operation limits."""
    return f"Deleted {len(user_ids)} users"


# =============================================================================
# Example 3: Human-in-the-Loop
# =============================================================================

@requires_approval(message="Approve deletion of production data?")
@agent
def delete_production_data(table: str):
    """Agent requiring human approval."""
    return f"Deleted table: {table}"


@human_feedback()
@agent
def draft_email(topic: str):
    """Agent requesting human feedback."""
    return f"Email draft about {topic}: Dear user, ..."


# =============================================================================
# Example 4: Memory
# =============================================================================

@with_memory(key="user_context")
@agent
def personalized_agent(user_id: str, message: str):
    """Agent with memory of past interactions."""
    return f"Personalized response for {user_id}: {message}"


# =============================================================================
# Example 5: Retry
# =============================================================================

@retry(max_attempts=3, delay=0.5)
@agent
def flaky_api_call(endpoint: str):
    """Agent with auto-retry."""
    import random
    if random.random() < 0.6:  # 60% chance of failure
        raise Exception("API temporary error")
    return f"Success: {endpoint}"


# =============================================================================
# Example 6: Planning
# =============================================================================

@plan_task(available_tools=["search", "analyze", "summarize"])
@agent
def research_with_plan(goal: str):
    """Agent that auto-plans execution."""
    return f"Completed research on: {goal}"


# =============================================================================
# Example 7: Stack Multiple Decorators
# =============================================================================

production_agent = stack(
    retry(max_attempts=3),
    requires_approval(),
    with_memory(),
    log_execution(),
    guardrail(severity="high")
)

@production_agent
@agent
def production_ready_agent(task: str):
    """Agent with ALL production features - one decorator stack!"""
    return f"Completed: {task}"


# =============================================================================
# Example 8: Mix and Match
# =============================================================================

@log_execution()
@validate(lambda r: r is not None)
@retry(max_attempts=2)
@agent
def robust_agent(query: str):
    """Mix multiple decorators as needed."""
    return f"Robust processing: {query}"


# =============================================================================
# Run Examples
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("AAF Feature Decorators - Lambda Simplicity Everywhere!")
    print("="*60)
    
    # Example 1: Validated agent
    print("\n1️⃣ Validated Agent:")
    result = validated_researcher("quantum computing")
    print(f"   Result: {result}")
    
    # Example 2: Guardrails
    print("\n2️⃣ Guardrails:")
    try:
        safe_delete(50)  # OK
        print("   ✅ Safe deletion succeeded")
    except:
        print("   ❌ Blocked by guardrail")
    
    try:
        safe_delete(200)  # Blocked!
        print("   ✅ Unsafe deletion succeeded (should not happen!)")
    except ValueError as e:
        print(f"   ✅ Blocked by guardrail: {e}")
    
    # Example 3: Bulk operations limit
    print("\n3️⃣ Bulk Operations Limit:")
    try:
        limited_delete(["user1", "user2", "user3"])  # OK
        print("   ✅ Small delete succeeded")
    except:
        print("   ❌ Blocked")
    
    try:
        limited_delete([f"user{i}" for i in range(60)])  # Blocked!
        print("   ❌ Large delete succeeded (should not happen!)")
    except ValueError as e:
        print(f"   ✅ Blocked: {e}")
    
    # Example 4: Memory
    print("\n4️⃣ Memory:")
    personalized_agent("user123", "Hello")
    personalized_agent("user123", "How are you?")
    print("   ✅ Agent remembers past interactions")
    
    # Example 5: Retry
    print("\n5️⃣ Retry:")
    try:
        result = flaky_api_call("/api/data")
        print(f"   ✅ Success after retries: {result}")
    except:
        print("   ❌ Failed after all retries")
    
    # Example 6: Planning
    print("\n6️⃣ Planning:")
    result = research_with_plan("AI trends 2025")
    print(f"   Plan steps: {len(result.get('plan', []))}")
    
    # Example 7: Logging
    print("\n7️⃣ Logging:")
    robust_agent("test query")
    
    print("\n" + "="*60)
    print("✨ All Features Available as Simple Decorators!")
    print("="*60)
    
    print("\n💡 Key Insight:")
    print("   - Just add @decorator - no boilerplate!")
    print("   - Stack decorators for complex behavior")
    print("   - Lambda-like simplicity for ALL features")
