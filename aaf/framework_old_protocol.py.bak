"""
Core framework implementation.

This module contains the orchestrator, adapter agent, and facade factory
that tie all the AAF components together.
"""

import logging
from typing import Dict, Any, List, Optional
from aaf.abstracts import (
    AbstractAgent,
    AbstractWorkflowOrchestrator,
    AbstractMiddleware,
    AbstractService,
    AbstractState,
)


class LangGraphAdapter:
    """
    Simplified LangGraph-inspired workflow orchestrator.
    
    Executes a linear workflow: applies middleware before/after each service call.
    In a real implementation, this would use LangGraph's state graph capabilities.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
    
    @property
    def orchestrator_name(self) -> str:
        return "langgraph_adapter"
    
    def execute_graph(
        self,
        state: AbstractState,
        services: List[AbstractService],
        middleware_stack: List[AbstractMiddleware]
    ) -> AbstractState:
        """
        Execute workflow graph by processing each service with middleware.
        
        Args:
            state: Initial agent state
            services: List of services to execute
            middleware_stack: Middleware to apply to each service call
            
        Returns:
            Final state after all services have been executed
        """
        self._logger.info(f"[{self.orchestrator_name}] Starting workflow execution")
        self._logger.debug(f"[{self.orchestrator_name}] Services to execute: {len(services)}")
        self._logger.debug(f"[{self.orchestrator_name}] Middleware stack: {[m.middleware_name for m in middleware_stack]}")
        
        for service in services:
            self._logger.info(f"[{self.orchestrator_name}] Processing service: {service.service_name}")
            
            working_state = state.copy()
            
            for middleware in middleware_stack:
                self._logger.debug(f"[{self.orchestrator_name}] Applying before_execute: {middleware.middleware_name}")
                working_state = middleware.before_execute(working_state, service)
            
            token = working_state.get('metadata', {}).get('injected_token')
            request = working_state.get('request', {})
            
            try:
                self._logger.debug(f"[{self.orchestrator_name}] Executing service: {service.service_name}")
                response = service.execute(request, token)
                working_state['response'] = response
                self._logger.info(f"[{self.orchestrator_name}] Service executed successfully: {service.service_name}")
            except Exception as e:
                self._logger.error(f"[{self.orchestrator_name}] Service execution failed: {service.service_name}")
                self._logger.error(f"[{self.orchestrator_name}] Error: {str(e)}")
                working_state['response'] = {
                    'status': 'error',
                    'error': str(e),
                    'service': service.service_name
                }
                raise
            
            for middleware in reversed(middleware_stack):
                self._logger.debug(f"[{self.orchestrator_name}] Applying after_execute: {middleware.middleware_name}")
                working_state = middleware.after_execute(working_state, service)
            
            state = working_state
        
        self._logger.info(f"[{self.orchestrator_name}] Workflow execution completed")
        return state


class AAFAdapterAgent:
    """
    Agent adapter that wraps core logic with middleware stack.
    
    This adapter applies the middleware pattern to agent execution,
    orchestrating service calls through the configured workflow engine.
    """
    
    def __init__(
        self,
        agent_id: str,
        orchestrator: AbstractWorkflowOrchestrator,
        services: List[AbstractService],
        middleware_stack: List[AbstractMiddleware],
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        self._agent_id = agent_id
        self._orchestrator = orchestrator
        self._services = services
        self._middleware_stack = middleware_stack
        self._config = config or {}
        self._logger = logger or logging.getLogger(__name__)
        self._initialized = False
    
    @property
    def agent_id(self) -> str:
        return self._agent_id
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the agent with configuration."""
        self._logger.info(f"[Agent {self.agent_id}] Initializing...")
        self._config.update(config)
        self._initialized = True
        self._logger.info(f"[Agent {self.agent_id}] Initialization complete")
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic with middleware stack.
        
        Args:
            input_data: Input data for execution
            
        Returns:
            Execution results
        """
        if not self._initialized:
            self.initialize({})
        
        self._logger.info(f"[Agent {self.agent_id}] Starting execution")
        
        state: AbstractState = {
            'agent_id': self._agent_id,
            'context': input_data.get('context', {}),
            'token_map': input_data.get('token_map', {}),
            'request': input_data.get('request', {}),
            'response': None,
            'metadata': {}
        }
        
        final_state = self._orchestrator.execute_graph(
            state,
            self._services,
            self._middleware_stack
        )
        
        self._logger.info(f"[Agent {self.agent_id}] Execution complete")
        
        return {
            'agent_id': final_state.get('agent_id'),
            'response': final_state.get('response'),
            'metadata': final_state.get('metadata', {})
        }
    
    def shutdown(self) -> None:
        """Clean up resources."""
        self._logger.info(f"[Agent {self.agent_id}] Shutting down...")
        self._initialized = False
        self._logger.info(f"[Agent {self.agent_id}] Shutdown complete")


class AgenticFrameworkX:
    """
    Central facade for the Agentic Application Framework.
    
    Provides factory methods to create configured agents with specified
    frameworks, services, and security settings.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
    
    def create_agent(
        self,
        agent_id: str,
        framework: str = "langgraph",
        services: Optional[List[AbstractService]] = None,
        security: bool = True,
        additional_middleware: Optional[List[AbstractMiddleware]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> AbstractAgent:
        """
        Factory method to create a configured agent.
        
        Args:
            agent_id: Unique identifier for the agent
            framework: Workflow framework to use ('langgraph' is currently supported)
            services: List of services the agent can use
            security: Whether to enable AuthMiddleware for token injection
            additional_middleware: Additional middleware to include in the stack
            config: Agent configuration
            
        Returns:
            Configured agent instance
            
        Raises:
            ValueError: If unsupported framework is specified
        """
        self._logger.info(f"[AgenticFrameworkX] Creating agent '{agent_id}'")
        self._logger.info(f"[AgenticFrameworkX] Framework: {framework}, Security: {security}")
        
        if framework == "langgraph":
            orchestrator = LangGraphAdapter(self._logger)
        else:
            raise ValueError(f"Unsupported framework: {framework}. Supported frameworks: ['langgraph']")
        
        from aaf.middleware import LoggingMiddleware, AuthMiddleware
        
        middleware_stack: List[AbstractMiddleware] = []
        
        middleware_stack.append(LoggingMiddleware(self._logger))
        
        if security:
            self._logger.info("[AgenticFrameworkX] Security enabled - adding AuthMiddleware")
            middleware_stack.append(AuthMiddleware(self._logger))
        else:
            self._logger.info("[AgenticFrameworkX] Security disabled - AuthMiddleware not added")
        
        if additional_middleware:
            middleware_stack.extend(additional_middleware)
        
        services = services or []
        
        agent = AAFAdapterAgent(
            agent_id=agent_id,
            orchestrator=orchestrator,
            services=services,
            middleware_stack=middleware_stack,
            config=config,
            logger=self._logger
        )
        
        self._logger.info(f"[AgenticFrameworkX] Agent '{agent_id}' created successfully")
        return agent
