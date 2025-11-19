"""
Workflow node system for AAF - Build real agentic workflows with conditional routing.

This module provides decorators for creating workflow graphs with nodes,
state management, and conditional routing - similar to LangGraph but simpler.
"""

from typing import Callable, Dict, Any, Optional, List, Union
from functools import wraps
import logging

logger = logging.getLogger(__name__)


# Global registry for workflow nodes
_NODE_REGISTRY: Dict[str, "WorkflowNode"] = {}


class WorkflowNode:
    """
    A node in a workflow graph.
    
    Nodes are steps in a workflow that process state and return updated state.
    """
    
    def __init__(
        self,
        func: Callable,
        node_id: str,
        description: Optional[str] = None
    ):
        self.func = func
        self.node_id = node_id
        self.description = description or func.__doc__ or f"Node: {node_id}"
        self._wrapped_functions = []  # For stacked decorators like @llm, @mcp_tool
    
    def add_wrapper(self, wrapper_func: Callable):
        """Add a wrapper function (from decorators like @llm)."""
        self._wrapped_functions.append(wrapper_func)
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node with the given state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state after node execution
        """
        logger.info(f"[Node:{self.node_id}] Executing...")
        
        try:
            # Execute the function (it may be wrapped by @llm, @mcp_tool, etc.)
            result = self.func(state)
            
            # If result is a dict, merge it into state
            if isinstance(result, dict):
                updated_state = {**state, **result}
            else:
                # If not a dict, store in 'result' key
                updated_state = {**state, "result": result}
            
            logger.info(f"[Node:{self.node_id}] Completed successfully")
            return updated_state
            
        except Exception as e:
            logger.error(f"[Node:{self.node_id}] Failed: {e}")
            return {**state, "error": str(e), "failed_node": self.node_id}
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Allow calling node directly."""
        return self.execute(state)
    
    def __repr__(self):
        return f"<WorkflowNode '{self.node_id}'>"


def node(
    node_id: Optional[str] = None,
    description: Optional[str] = None
):
    """
    Decorator to mark a function as a workflow node.
    
    Nodes are steps in a workflow graph that process state.
    
    Example:
        @node
        def parse_intent(state):
            query = state["user_query"]
            # Determine intent
            return {"intent": "database"}
        
        @node
        @llm(model="openai:gpt-4")
        def generate_sql(state):
            query = state["user_query"]
            return {"sql": "SELECT * FROM users"}
        
        @node(node_id="custom_node", description="Custom processing")
        def custom_step(state):
            return {"processed": True}
    
    Args:
        node_id: Optional custom node ID (defaults to function name)
        description: Optional description of what this node does
    """
    # Handle both @node and @node() syntax
    if callable(node_id):
        # Called as @node without parentheses
        func = node_id
        node_id = None
        return _create_node(func, None, None)
    
    def decorator(func: Callable):
        return _create_node(func, node_id, description)
    
    return decorator


def _create_node(
    func: Callable,
    node_id: Optional[str],
    description: Optional[str]
) -> WorkflowNode:
    """Internal function to create a workflow node."""
    _node_id = node_id or func.__name__
    
    # Create the node
    workflow_node = WorkflowNode(
        func=func,
        node_id=_node_id,
        description=description
    )
    
    # Register it
    _NODE_REGISTRY[_node_id] = workflow_node
    
    return workflow_node


class WorkflowGraph:
    """
    A workflow graph with nodes and conditional routing.
    
    This is similar to LangGraph but simpler and decorator-based.
    """
    
    def __init__(
        self,
        start_node: str,
        nodes: Dict[str, WorkflowNode],
        routing: Dict[str, Union[str, Callable]],
        end_node: Optional[str] = None
    ):
        """
        Initialize workflow graph.
        
        Args:
            start_node: ID of the starting node
            nodes: Dictionary of node_id -> WorkflowNode
            routing: Dictionary mapping node_id -> next_node_id or routing function
            end_node: Optional node that marks the end of workflow
        """
        self.start_node = start_node
        self.nodes = nodes
        self.routing = routing
        self.end_node = end_node
    
    def execute(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the workflow graph.
        
        Args:
            initial_state: Initial state to start the workflow
            
        Returns:
            Final state after workflow completion
        """
        logger.info(f"[WorkflowGraph] Starting execution from node: {self.start_node}")
        
        current_node_id = self.start_node
        state = initial_state.copy()
        visited_nodes = []
        max_iterations = 100  # Prevent infinite loops
        iterations = 0
        
        while current_node_id and iterations < max_iterations:
            # Check if we've reached the end
            if current_node_id == self.end_node:
                logger.info(f"[WorkflowGraph] Reached end node: {self.end_node}")
                break
            
            # Get current node
            if current_node_id not in self.nodes:
                raise ValueError(f"Node '{current_node_id}' not found in graph")
            
            current_node = self.nodes[current_node_id]
            visited_nodes.append(current_node_id)
            
            # Execute node
            state = current_node.execute(state)
            
            # Check for errors
            if "error" in state:
                logger.error(f"[WorkflowGraph] Error in node {current_node_id}: {state['error']}")
                break
            
            # Determine next node
            if current_node_id not in self.routing:
                # No routing defined - end here
                logger.info(f"[WorkflowGraph] No routing from {current_node_id}, ending")
                break
            
            routing_rule = self.routing[current_node_id]
            
            # Handle different routing types
            if callable(routing_rule):
                # Routing function - decides next node based on state
                next_node_id = routing_rule(state)
                logger.info(f"[WorkflowGraph] Routing function chose: {next_node_id}")
            elif isinstance(routing_rule, str):
                # Static routing - always go to this node
                next_node_id = routing_rule
                logger.info(f"[WorkflowGraph] Static routing to: {next_node_id}")
            elif isinstance(routing_rule, dict):
                # Conditional routing - map state values to nodes
                # e.g., {"intent": {"database": "generate_sql", "tool": "call_tool"}}
                condition_key = list(routing_rule.keys())[0]
                condition_value = state.get(condition_key)
                next_node_id = routing_rule[condition_key].get(condition_value)
                logger.info(f"[WorkflowGraph] Conditional routing ({condition_key}={condition_value}): {next_node_id}")
            else:
                raise ValueError(f"Invalid routing rule type: {type(routing_rule)}")
            
            current_node_id = next_node_id
            iterations += 1
        
        if iterations >= max_iterations:
            logger.warning(f"[WorkflowGraph] Max iterations reached ({max_iterations})")
        
        logger.info(f"[WorkflowGraph] Completed. Visited nodes: {visited_nodes}")
        
        state["_visited_nodes"] = visited_nodes
        state["_final_node"] = current_node_id or visited_nodes[-1] if visited_nodes else None
        
        return state
    
    def __call__(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Allow calling graph directly."""
        return self.execute(initial_state)


def workflow_graph(
    start: str,
    routing: Dict[str, Union[str, Callable]],
    end: Optional[str] = None
):
    """
    Decorator to create a workflow graph from nodes.
    
    Example:
        @node
        def parse_intent(state):
            return {"intent": "database"}
        
        @node
        def generate_sql(state):
            return {"sql": "SELECT ..."}
        
        @node
        def call_tool(state):
            return {"result": "..."}
        
        @workflow_graph(
            start="parse_intent",
            routing={
                "parse_intent": lambda state: "generate_sql" if state["intent"] == "database" else "call_tool",
                "generate_sql": "END",
                "call_tool": "END"
            },
            end="END"
        )
        def chat_workflow(user_query: str):
            return {"user_query": user_query}
        
        # Use it
        result = chat_workflow("Show me users")
        print(result["sql"])
    """
    def decorator(func: Callable):
        # Extract nodes from routing
        node_ids = set([start])
        for from_node, to_node in routing.items():
            node_ids.add(from_node)
            if isinstance(to_node, str) and to_node != end:
                node_ids.add(to_node)
        
        # Get nodes from registry
        nodes = {}
        for node_id in node_ids:
            if node_id == end:
                continue
            if node_id not in _NODE_REGISTRY:
                raise ValueError(f"Node '{node_id}' not found. Did you forget @node decorator?")
            nodes[node_id] = _NODE_REGISTRY[node_id]
        
        # Create workflow graph
        graph = WorkflowGraph(
            start_node=start,
            nodes=nodes,
            routing=routing,
            end_node=end
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get initial state from the function
            initial_state = func(*args, **kwargs)
            
            # Execute workflow
            return graph.execute(initial_state)
        
        # Attach graph for inspection
        wrapper.graph = graph
        
        return wrapper
    
    return decorator


def get_node(node_id: str) -> Optional[WorkflowNode]:
    """Get a registered node by ID."""
    return _NODE_REGISTRY.get(node_id)


def list_nodes() -> List[str]:
    """List all registered node IDs."""
    return list(_NODE_REGISTRY.keys())
