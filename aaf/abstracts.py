"""
Core abstractions for the Agentic Application Framework.

This module defines the Protocol contracts and TypedDict schemas that establish
the framework's interface contracts.
"""

from typing import Protocol, TypedDict, Any, Dict, List, Optional, Callable
from abc import abstractmethod


class AbstractState(TypedDict, total=False):
    """
    State container for agent execution context.
    
    Attributes:
        agent_id: Unique identifier for the agent instance
        context: Arbitrary context data for the agent's execution
        token_map: Mapping of service names to authentication tokens
        request: The current request payload being processed
        response: The response payload after processing
        metadata: Additional metadata for tracking and debugging
    """
    agent_id: str
    context: Dict[str, Any]
    token_map: Dict[str, str]
    request: Dict[str, Any]
    response: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]


class AbstractService(Protocol):
    """
    Protocol for external service integrations.
    
    Services represent external interfaces (MCP tools, A2A agents, etc.)
    that require authentication and have specific execution semantics.
    """
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the unique name of this service."""
        ...
    
    @property
    @abstractmethod
    def requires_token(self) -> bool:
        """Indicate whether this service requires authentication token."""
        ...
    
    @abstractmethod
    def execute(self, request: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a service operation.
        
        Args:
            request: The request payload containing operation parameters
            token: Optional authentication token (required if requires_token is True)
            
        Returns:
            Response payload from the service
            
        Raises:
            PermissionError: If token is required but not provided or invalid
        """
        ...


class AbstractMiddleware(Protocol):
    """
    Protocol for middleware components that intercept and transform requests/responses.
    
    Middleware can modify state, inject dependencies, log operations, enforce policies, etc.
    """
    
    @property
    @abstractmethod
    def middleware_name(self) -> str:
        """Return the unique name of this middleware."""
        ...
    
    @abstractmethod
    def before_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Hook executed before service execution.
        
        Args:
            state: Current agent state
            service: The service about to be executed
            
        Returns:
            Modified state (can modify request, inject tokens, etc.)
        """
        ...
    
    @abstractmethod
    def after_execute(self, state: AbstractState, service: AbstractService) -> AbstractState:
        """
        Hook executed after service execution.
        
        Args:
            state: Current agent state with response populated
            service: The service that was executed
            
        Returns:
            Modified state (can transform response, log results, etc.)
        """
        ...


class AbstractWorkflowOrchestrator(Protocol):
    """
    Protocol for workflow orchestration engines.
    
    Orchestrators manage the execution graph and coordinate service calls.
    """
    
    @property
    @abstractmethod
    def orchestrator_name(self) -> str:
        """Return the name of this orchestrator."""
        ...
    
    @abstractmethod
    def execute_graph(
        self, 
        state: AbstractState, 
        services: List[AbstractService],
        middleware_stack: List[AbstractMiddleware]
    ) -> AbstractState:
        """
        Execute the workflow graph.
        
        Args:
            state: Initial agent state
            services: Available services for the agent
            middleware_stack: Middleware components to apply
            
        Returns:
            Final state after workflow execution
        """
        ...


class AbstractAgent(Protocol):
    """
    Protocol for agent instances.
    
    Agents have lifecycle hooks and maintain state during execution.
    """
    
    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Return the unique identifier for this agent."""
        ...
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the agent with configuration.
        
        Args:
            config: Configuration parameters for agent setup
        """
        ...
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic.
        
        Args:
            input_data: Input data for agent execution
            
        Returns:
            Execution results
        """
        ...
    
    @abstractmethod
    def shutdown(self) -> None:
        """Clean up resources and shutdown the agent."""
        ...


class MemoryEntry(TypedDict, total=False):
    """
    Memory entry for storing agent memories.
    
    Attributes:
        id: Unique identifier for the memory entry
        content: The memory content (text, data, etc.)
        embedding: Optional vector embedding for semantic search
        metadata: Additional metadata (timestamp, source, etc.)
        relevance_score: Score for memory relevance/importance
    """
    id: str
    content: Any
    embedding: Optional[List[float]]
    metadata: Dict[str, Any]
    relevance_score: float


class AbstractMemory(Protocol):
    """
    Protocol for memory storage and retrieval.
    
    Memory systems enable agents to store and recall information across
    interactions, supporting both short-term (working memory) and long-term
    (persistent semantic memory) use cases.
    """
    
    @property
    @abstractmethod
    def memory_name(self) -> str:
        """Return the name of this memory system."""
        ...
    
    @abstractmethod
    def add(self, entry: MemoryEntry) -> bool:
        """
        Add a memory entry.
        
        Args:
            entry: Memory entry to store
            
        Returns:
            True if successfully added
        """
        ...
    
    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """
        Search for relevant memories.
        
        Args:
            query: Search query (text or semantic)
            limit: Maximum number of results
            metadata_filter: Optional filter for metadata fields
            
        Returns:
            List of relevant memory entries, ordered by relevance
        """
        ...
    
    @abstractmethod
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Get a specific memory by ID.
        
        Args:
            memory_id: Unique identifier for the memory
            
        Returns:
            Memory entry if found, None otherwise
        """
        ...
    
    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            memory_id: Unique identifier for the memory
            
        Returns:
            True if successfully deleted
        """
        ...
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all memories.
        
        Returns:
            True if successfully cleared
        """
        ...


class AbstractPlanner(Protocol):
    """
    Protocol for task planning and decomposition.
    
    Planners break down complex goals into executable sub-tasks and
    determine the optimal execution strategy.
    """
    
    @property
    @abstractmethod
    def planner_name(self) -> str:
        """Return the name of this planner."""
        ...
    
    @abstractmethod
    def create_plan(
        self,
        goal: str,
        context: Dict[str, Any],
        available_services: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Create an execution plan for a given goal.
        
        Args:
            goal: The high-level objective to achieve
            context: Contextual information for planning
            available_services: List of available service names
            
        Returns:
            List of planned steps, each with action and parameters
        """
        ...
    
    @abstractmethod
    def refine_plan(
        self,
        plan: List[Dict[str, Any]],
        feedback: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Refine an existing plan based on feedback.
        
        Args:
            plan: Current execution plan
            feedback: Feedback from execution or user
            
        Returns:
            Refined execution plan
        """
        ...


class AbstractReasoner(Protocol):
    """
    Protocol for reasoning and decision-making.
    
    Reasoners implement patterns like ReAct (Reason + Act) to combine
    logical reasoning with action execution.
    """
    
    @property
    @abstractmethod
    def reasoner_name(self) -> str:
        """Return the name of this reasoner."""
        ...
    
    @abstractmethod
    def reason(
        self,
        observation: str,
        history: List[Dict[str, Any]],
        goal: str
    ) -> Dict[str, Any]:
        """
        Reason about the current state and determine next action.
        
        Args:
            observation: Current observation or feedback
            history: History of previous reasoning steps
            goal: The objective to achieve
            
        Returns:
            Reasoning result with thought process and next action
        """
        ...
