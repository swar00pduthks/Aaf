"""
Middleware implementations for request/response processing.

This module provides pluggable middleware components that can intercept
and transform service calls.
"""

import logging
from typing import Dict, Any, Optional
from aaf.abstracts import AbstractMiddleware, AbstractService, AbstractState


class LoggingMiddleware:
    """
    Middleware that logs service execution details.
    
    Logs before and after service execution for debugging and monitoring.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def middleware_name(self) -> str:
        return "logging_middleware"
    
    def before_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Log request details before service execution.
        
        Args:
            state: Current agent state
            service: Service about to be executed
            
        Returns:
            Unmodified state
        """
        self._logger.info(f"[BEFORE] Executing service: {service.service_name}")
        self._logger.debug(f"[BEFORE] Request payload: {state.get('request', {})}")
        self._logger.debug(f"[BEFORE] Agent ID: {state.get('agent_id', 'unknown')}")
        
        if 'metadata' not in state:
            state['metadata'] = {}
        state['metadata']['logging_enabled'] = True
        
        return state
    
    def after_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Log response details after service execution.
        
        Args:
            state: Current agent state with response
            service: Service that was executed
            
        Returns:
            Unmodified state
        """
        self._logger.info(f"[AFTER] Completed service: {service.service_name}")
        
        response = state.get('response')
        if response:
            status = response.get('status', 'unknown')
            self._logger.info(f"[AFTER] Response status: {status}")
            self._logger.debug(f"[AFTER] Response payload: {response}")
        else:
            self._logger.warning(f"[AFTER] No response found in state for service: {service.service_name}")
        
        return state


class AuthMiddleware:
    """
    Middleware that manages authentication token injection.
    
    Reads tokens from the agent's token_map and injects them into service calls
    that require authentication.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def middleware_name(self) -> str:
        return "auth_middleware"
    
    def before_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Inject authentication token from token_map if service requires it.
        
        Args:
            state: Current agent state
            service: Service about to be executed
            
        Returns:
            Modified state with token injected into metadata
        """
        if not service.requires_token:
            self._logger.debug(f"[AUTH] Service '{service.service_name}' does not require token")
            return state
        
        token_map = state.get('token_map', {})
        
        if not token_map:
            self._logger.warning(
                f"[AUTH] Service '{service.service_name}' requires token but token_map is empty"
            )
            return state
        
        token = token_map.get(service.service_name)
        
        if token:
            self._logger.info(f"[AUTH] Token found for service '{service.service_name}', injecting...")
            
            if 'metadata' not in state:
                state['metadata'] = {}
            state['metadata']['injected_token'] = token
            
            self._logger.debug(f"[AUTH] Token injected successfully: {token[:10]}...")
        else:
            self._logger.warning(
                f"[AUTH] Service '{service.service_name}' requires token but no token found in token_map. "
                f"Available services in token_map: {list(token_map.keys())}"
            )
        
        return state
    
    def after_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Clean up authentication metadata after execution.
        
        Args:
            state: Current agent state with response
            service: Service that was executed
            
        Returns:
            State with auth metadata cleaned up
        """
        metadata = state.get('metadata', {})
        if 'injected_token' in metadata:
            self._logger.debug(f"[AUTH] Cleaning up injected token for service '{service.service_name}'")
            del metadata['injected_token']
        
        return state
