"""
Agent registry for managing agent lifecycle and discovery.

This module provides a centralized registry for agent instances,
enabling agent lookup, lifecycle management, and monitoring.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from aaf.abstracts import AbstractAgent


class AgentInfo:
    """
    Information about a registered agent.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent: AbstractAgent,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.agent_id = agent_id
        self.agent = agent
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.last_accessed = self.created_at
        self.execution_count = 0
        self.status = "initialized"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent info to dictionary."""
        return {
            "agent_id": self.agent_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "execution_count": self.execution_count,
            "status": self.status
        }


class AgentRegistry:
    """
    Centralized registry for agent lifecycle management.
    
    Provides agent registration, lookup, and lifecycle tracking.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
        self._agents: Dict[str, AgentInfo] = {}
        self._logger.info("[AgentRegistry] Initialized")
    
    def register(
        self,
        agent_id: str,
        agent: AbstractAgent,
        metadata: Optional[Dict[str, Any]] = None,
        replace: bool = False
    ) -> bool:
        """
        Register an agent in the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance to register
            metadata: Optional metadata about the agent
            replace: Whether to replace existing agent with same ID
            
        Returns:
            True if registration was successful
            
        Raises:
            ValueError: If agent_id already exists and replace=False
        """
        is_replacing = agent_id in self._agents
        
        if is_replacing and not replace:
            raise ValueError(
                f"Agent '{agent_id}' already registered. Use replace=True to override."
            )
        
        agent_info = AgentInfo(agent_id, agent, metadata)
        self._agents[agent_id] = agent_info
        
        action = "Replaced" if is_replacing else "Registered"
        self._logger.info(f"[AgentRegistry] {action} agent '{agent_id}'")
        
        return True
    
    def get(self, agent_id: str) -> Optional[AbstractAgent]:
        """
        Get an agent from the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Agent instance if found, None otherwise
        """
        agent_info = self._agents.get(agent_id)
        
        if agent_info:
            agent_info.last_accessed = datetime.utcnow()
            self._logger.debug(f"[AgentRegistry] Retrieved agent '{agent_id}'")
            return agent_info.agent
        else:
            self._logger.warning(f"[AgentRegistry] Agent '{agent_id}' not found")
            return None
    
    def unregister(self, agent_id: str, shutdown: bool = True) -> bool:
        """
        Unregister an agent from the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            shutdown: Whether to call shutdown() on the agent
            
        Returns:
            True if unregistration was successful
        """
        if agent_id not in self._agents:
            self._logger.warning(f"[AgentRegistry] Cannot unregister - agent '{agent_id}' not found")
            return False
        
        agent_info = self._agents[agent_id]
        
        if shutdown:
            try:
                agent_info.agent.shutdown()
                self._logger.info(f"[AgentRegistry] Shut down agent '{agent_id}'")
            except Exception as e:
                self._logger.error(f"[AgentRegistry] Error shutting down agent '{agent_id}': {str(e)}")
        
        del self._agents[agent_id]
        self._logger.info(f"[AgentRegistry] Unregistered agent '{agent_id}'")
        
        return True
    
    def list_agents(self) -> List[str]:
        """
        List all registered agent IDs.
        
        Returns:
            List of agent IDs
        """
        return list(self._agents.keys())
    
    def get_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered agent.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Agent information dictionary if found, None otherwise
        """
        agent_info = self._agents.get(agent_id)
        return agent_info.to_dict() if agent_info else None
    
    def get_all_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all registered agents.
        
        Returns:
            Dictionary mapping agent IDs to their info
        """
        return {
            agent_id: info.to_dict()
            for agent_id, info in self._agents.items()
        }
    
    def update_status(self, agent_id: str, status: str) -> bool:
        """
        Update the status of a registered agent.
        
        Args:
            agent_id: Unique identifier for the agent
            status: New status value
            
        Returns:
            True if update was successful
        """
        agent_info = self._agents.get(agent_id)
        
        if agent_info:
            agent_info.status = status
            self._logger.debug(f"[AgentRegistry] Updated status for agent '{agent_id}' to '{status}'")
            return True
        else:
            self._logger.warning(f"[AgentRegistry] Cannot update status - agent '{agent_id}' not found")
            return False
    
    def increment_execution_count(self, agent_id: str) -> None:
        """
        Increment execution count for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
        """
        agent_info = self._agents.get(agent_id)
        if agent_info:
            agent_info.execution_count += 1
    
    def shutdown_all(self) -> None:
        """Shutdown all registered agents."""
        self._logger.info("[AgentRegistry] Shutting down all agents...")
        
        for agent_id in list(self._agents.keys()):
            self.unregister(agent_id, shutdown=True)
        
        self._logger.info("[AgentRegistry] All agents shut down")
