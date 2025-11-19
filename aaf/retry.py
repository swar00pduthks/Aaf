"""
Retry logic implementations for the Agentic Application Framework.

This module provides retry policies and middleware for handling transient
failures in service calls, particularly for MCP tools and external APIs.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from functools import wraps
from aaf.abstracts import AbstractMiddleware, AbstractService, AbstractState


class RetryPolicy:
    """
    Configurable retry policy with exponential backoff.
    
    Implements exponential backoff with jitter to prevent thundering herd problems.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self._logger = logger or logging.getLogger(__name__)
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given retry attempt.
        
        Args:
            attempt: Current retry attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay
    
    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """
        Determine if a retry should be attempted.
        
        Args:
            attempt: Current retry attempt number (0-indexed)
            exception: Exception that occurred
            
        Returns:
            True if retry should be attempted
        """
        if attempt >= self.max_retries:
            return False
        
        if isinstance(exception, PermissionError):
            return False
        
        return True


class RetryMiddleware:
    """
    Middleware that adds retry logic to service calls.
    
    Wraps service execution with configurable retry policy, automatically
    retrying on transient failures.
    """
    
    def __init__(
        self,
        retry_policy: Optional[RetryPolicy] = None,
        logger: Optional[logging.Logger] = None
    ):
        self._retry_policy = retry_policy or RetryPolicy()
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def middleware_name(self) -> str:
        return "retry_middleware"
    
    def before_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Set up retry context before execution.
        
        Args:
            state: Current agent state
            service: Service about to be executed
            
        Returns:
            State with retry metadata
        """
        if 'metadata' not in state:
            state['metadata'] = {}
        
        state['metadata']['retry_enabled'] = True
        state['metadata']['retry_attempt'] = 0
        
        self._logger.debug(f"[RETRY] Retry enabled for service '{service.service_name}'")
        return state
    
    def after_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Clean up retry metadata after execution.
        
        Args:
            state: Current agent state
            service: Service that was executed
            
        Returns:
            Cleaned state
        """
        metadata = state.get('metadata', {})
        if 'retry_attempt' in metadata:
            attempts = metadata.get('retry_attempt', 0)
            if attempts > 0:
                self._logger.info(
                    f"[RETRY] Service '{service.service_name}' succeeded after {attempts} retries"
                )
            del metadata['retry_attempt']
        
        return state
    
    def execute_with_retry(
        self,
        service: AbstractService,
        request: Dict[str, Any],
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute service with retry logic.
        
        Args:
            service: Service to execute
            request: Request payload
            token: Optional authentication token
            
        Returns:
            Service response
            
        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(self._retry_policy.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self._retry_policy.calculate_delay(attempt - 1)
                    self._logger.info(
                        f"[RETRY] Attempt {attempt + 1}/{self._retry_policy.max_retries + 1} "
                        f"for service '{service.service_name}' after {delay:.2f}s delay"
                    )
                    time.sleep(delay)
                
                response = service.execute(request, token)
                
                if attempt > 0:
                    self._logger.info(
                        f"[RETRY] Service '{service.service_name}' succeeded on attempt {attempt + 1}"
                    )
                
                return response
                
            except Exception as e:
                last_exception = e
                
                if not self._retry_policy.should_retry(attempt, e):
                    self._logger.error(
                        f"[RETRY] Service '{service.service_name}' failed - not retrying: {str(e)}"
                    )
                    raise e
                
                self._logger.warning(
                    f"[RETRY] Service '{service.service_name}' failed on attempt {attempt + 1}: {str(e)}"
                )
        
        self._logger.error(
            f"[RETRY] Service '{service.service_name}' exhausted all {self._retry_policy.max_retries} retries"
        )
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError(f"Service '{service.service_name}' failed with no exception captured")


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    logger: Optional[logging.Logger] = None
):
    """
    Decorator to add retry logic to functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        logger: Optional logger instance
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_policy = RetryPolicy(
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                logger=logger
            )
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        delay = retry_policy.calculate_delay(attempt - 1)
                        time.sleep(delay)
                    
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    if not retry_policy.should_retry(attempt, e):
                        raise e
            
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Function failed with no exception captured")
        
        return wrapper
    return decorator
