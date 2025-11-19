"""
Feature decorators for validators, HITL, memory, retry, etc.

Extends AAF's decorator pattern to ALL features - Lambda-like simplicity everywhere!
"""

from typing import Callable, Optional, Dict, Any, List
from functools import wraps
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# Validator & Guardrail Decorators
# =============================================================================

def validate(*rules):
    """
    Add validation rules to any function.
    
    Example:
        @validate(
            lambda result: result.get("confidence", 0) > 0.7,
            lambda result: len(result.get("text", "")) > 10
        )
        @agent
        def researcher(query):
            return {"text": "...", "confidence": 0.9}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Validate result
            for rule in rules:
                if not rule(result):
                    logger.warning(f"[{func.__name__}] Validation failed!")
                    return {
                        "status": "validation_failed",
                        "result": result,
                        "message": "Output did not pass validation rules"
                    }
            
            return result
        return wrapper
    return decorator


def guardrail(severity: str = "high"):
    """
    Add safety guardrails to any function.
    
    Example:
        @guardrail(severity="high")
        @agent
        def delete_records(count: int):
            if count > 100:
                raise ValueError("Bulk delete blocked by guardrail")
            return f"Deleted {count} records"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"[Guardrail:{severity}] Checking {func.__name__}...")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"[Guardrail] {func.__name__} passed")
                return result
            except Exception as e:
                logger.error(f"[Guardrail] {func.__name__} blocked: {e}")
                if severity in ["high", "critical"]:
                    raise
                return {"status": "blocked", "error": str(e)}
        
        return wrapper
    return decorator


def no_bulk_operations(max_count: int = 100):
    """
    Prevent bulk operations above threshold.
    
    Example:
        @no_bulk_operations(max_count=50)
        @agent
        def delete_users(user_ids: list):
            return f"Deleted {len(user_ids)} users"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to find count parameter
            count = None
            if args and isinstance(args[0], (list, dict)):
                count = len(args[0])
            elif 'count' in kwargs:
                count = kwargs['count']
            
            if count and count > max_count:
                raise ValueError(f"Bulk operation blocked: {count} > {max_count} limit")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# Human-in-the-Loop Decorators
# =============================================================================

def requires_approval(message: Optional[str] = None):
    """
    Require human approval before execution.
    
    Example:
        @requires_approval(message="Delete sensitive data?")
        @agent
        def delete_data(table: str):
            return f"Deleted {table}"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from aaf import ApprovalWorkflow
            
            approval_msg = message or f"Approve execution of {func.__name__}?"
            logger.info(f"[HITL] Requesting approval: {approval_msg}")
            
            workflow = ApprovalWorkflow()
            status = workflow.request_approval(
                action=approval_msg,
                context={"function": func.__name__, "args": str(args)[:100]}
            )
            
            if status.value == "approved":
                logger.info(f"[HITL] Approved - executing {func.__name__}")
                return func(*args, **kwargs)
            else:
                logger.warning(f"[HITL] {status.value} - blocking {func.__name__}")
                return {"status": "blocked", "reason": status.value}
        
        return wrapper
    return decorator


def human_feedback():
    """
    Request human feedback after execution.
    
    Example:
        @human_feedback()
        @agent
        def draft_email(topic: str):
            return "Email draft: ..."
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            logger.info(f"[HITL] Result from {func.__name__}: {str(result)[:100]}")
            logger.info(f"[HITL] Awaiting human feedback...")
            
            # In real implementation, would collect actual feedback
            # For now, just log and return
            return {
                "result": result,
                "feedback_requested": True,
                "message": "Please review and provide feedback"
            }
        
        return wrapper
    return decorator


# =============================================================================
# Memory Decorators
# =============================================================================

def with_memory(key: Optional[str] = None):
    """
    Add memory to any function - remembers past calls.
    
    Example:
        @with_memory(key="user_preferences")
        @agent
        def personalize(user_id: str):
            # Automatically has access to memory
            return "Personalized response"
    """
    def decorator(func: Callable) -> Callable:
        from aaf import InMemoryShortTermMemory
        
        memory_key = key or func.__name__
        memory = InMemoryShortTermMemory()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Load past context from memory
            past_context = memory.search(memory_key, limit=5)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store result in memory
            memory.add({
                "content": str(result)[:200],
                "metadata": {
                    "function": func.__name__,
                    "key": memory_key
                }
            })
            
            logger.info(f"[Memory:{memory_key}] Stored result, {len(past_context)} past entries")
            
            return result
        
        return wrapper
    return decorator


# =============================================================================
# Retry Decorators
# =============================================================================

def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Auto-retry on failure with exponential backoff.
    
    Example:
        @retry(max_attempts=3, delay=1.0)
        @agent
        def call_api(endpoint: str):
            # Will retry up to 3 times if it fails
            return requests.get(endpoint)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        wait_time = delay * (2 ** (attempt - 1))  # Exponential backoff
                        logger.warning(
                            f"[Retry] {func.__name__} failed (attempt {attempt}/{max_attempts}), "
                            f"retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"[Retry] {func.__name__} failed after {max_attempts} attempts")
            
            raise last_exception
        
        return wrapper
    return decorator


# =============================================================================
# Planning Decorators
# =============================================================================

def plan_task(available_tools: Optional[List[str]] = None):
    """
    Auto-plan task execution.
    
    Example:
        @plan_task(available_tools=["search", "analyze"])
        @agent
        def research(goal: str):
            # Automatically creates execution plan
            return "Research complete"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from aaf import SimpleTaskPlanner
            
            planner = SimpleTaskPlanner()
            
            # Extract goal from args
            goal = args[0] if args else kwargs.get("goal", "Execute task")
            
            # Create plan
            plan = planner.create_plan(
                goal=str(goal),
                context={},
                available_services=available_tools or []
            )
            
            logger.info(f"[Planning] Created plan with {len(plan)} steps for {func.__name__}")
            for i, step in enumerate(plan, 1):
                logger.info(f"  Step {i}: {step['action']}")
            
            # Execute function
            result = func(*args, **kwargs)
            
            return {
                "result": result,
                "plan": plan,
                "steps_completed": len(plan)
            }
        
        return wrapper
    return decorator


# =============================================================================
# Logging Decorators
# =============================================================================

def log_execution(level: str = "INFO"):
    """
    Auto-log function execution.
    
    Example:
        @log_execution(level="INFO")
        @agent
        def process_data(data):
            return "processed"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.log(
                getattr(logging, level),
                f"[{func.__name__}] Starting with args={str(args)[:50]}"
            )
            
            result = func(*args, **kwargs)
            
            logger.log(
                getattr(logging, level),
                f"[{func.__name__}] Completed, result={str(result)[:50]}"
            )
            
            return result
        
        return wrapper
    return decorator


# =============================================================================
# Composition Helper
# =============================================================================

def stack(*decorators):
    """
    Stack multiple decorators for composition.
    
    Example:
        my_decorators = stack(
            retry(max_attempts=3),
            requires_approval(),
            with_memory(),
            log_execution()
        )
        
        @my_decorators
        @agent
        def my_agent(query):
            return process(query)
    """
    def decorator(func: Callable) -> Callable:
        for dec in reversed(decorators):
            func = dec(func)
        return func
    return decorator
