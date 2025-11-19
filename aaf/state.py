"""
State management implementations for the Agentic Application Framework.

This module provides state persistence and retrieval capabilities for agents,
enabling stateful execution across multiple invocations.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json


class InMemoryStateManager:
    """
    In-memory state manager for transient agent state storage.
    
    Suitable for development and single-instance deployments.
    State is lost when the process terminates.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
        self._state_store: Dict[str, Dict[str, Any]] = {}
        self._metadata_store: Dict[str, Dict[str, Any]] = {}
    
    @property
    def manager_name(self) -> str:
        return "in_memory_state_manager"
    
    def save_state(self, agent_id: str, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save agent state.
        
        Args:
            agent_id: Unique identifier for the agent
            state: State data to persist
            metadata: Optional metadata about the state
            
        Returns:
            True if save was successful
        """
        try:
            self._state_store[agent_id] = state.copy()
            
            meta = metadata or {}
            meta['last_updated'] = datetime.utcnow().isoformat()
            meta['version'] = meta.get('version', 0) + 1
            self._metadata_store[agent_id] = meta
            
            self._logger.info(f"[StateManager] Saved state for agent '{agent_id}' (version {meta['version']})")
            return True
        except Exception as e:
            self._logger.error(f"[StateManager] Failed to save state for agent '{agent_id}': {str(e)}")
            return False
    
    def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Load agent state.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            State data if found, None otherwise
        """
        if agent_id in self._state_store:
            state = self._state_store[agent_id]
            self._logger.info(f"[StateManager] Loaded state for agent '{agent_id}'")
            return state.copy()
        else:
            self._logger.warning(f"[StateManager] No state found for agent '{agent_id}'")
            return None
    
    def delete_state(self, agent_id: str) -> bool:
        """
        Delete agent state.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            True if deletion was successful
        """
        if agent_id in self._state_store:
            del self._state_store[agent_id]
            if agent_id in self._metadata_store:
                del self._metadata_store[agent_id]
            self._logger.info(f"[StateManager] Deleted state for agent '{agent_id}'")
            return True
        else:
            self._logger.warning(f"[StateManager] No state to delete for agent '{agent_id}'")
            return False
    
    def get_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata about stored state.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Metadata if found, None otherwise
        """
        return self._metadata_store.get(agent_id)
    
    def list_agents(self) -> list[str]:
        """
        List all agents with stored state.
        
        Returns:
            List of agent IDs
        """
        return list(self._state_store.keys())
    
    def clear_all(self) -> None:
        """Clear all stored state (use with caution)."""
        self._state_store.clear()
        self._metadata_store.clear()
        self._logger.warning("[StateManager] Cleared all stored state")


class FileStateManager:
    """
    File-based state manager for persistent agent state storage.
    
    Suitable for production deployments where state needs to persist
    across process restarts.
    """
    
    def __init__(self, storage_dir: str = "./agent_states", logger: Optional[logging.Logger] = None):
        import os
        self._logger = logger or logging.getLogger(__name__)
        self._storage_dir = storage_dir
        
        os.makedirs(storage_dir, exist_ok=True)
        self._logger.info(f"[FileStateManager] Initialized with storage directory: {storage_dir}")
    
    @property
    def manager_name(self) -> str:
        return "file_state_manager"
    
    def _get_file_path(self, agent_id: str) -> str:
        """Get file path for agent state."""
        import os
        safe_id = agent_id.replace('/', '_').replace('\\', '_')
        return os.path.join(self._storage_dir, f"{safe_id}.json")
    
    def save_state(self, agent_id: str, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Save agent state to file."""
        try:
            file_path = self._get_file_path(agent_id)
            
            meta = metadata or {}
            meta['last_updated'] = datetime.utcnow().isoformat()
            meta['agent_id'] = agent_id
            
            data = {
                'state': state,
                'metadata': meta
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self._logger.info(f"[FileStateManager] Saved state for agent '{agent_id}' to {file_path}")
            return True
        except Exception as e:
            self._logger.error(f"[FileStateManager] Failed to save state for agent '{agent_id}': {str(e)}")
            return False
    
    def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent state from file."""
        try:
            file_path = self._get_file_path(agent_id)
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self._logger.info(f"[FileStateManager] Loaded state for agent '{agent_id}'")
            return data.get('state')
        except FileNotFoundError:
            self._logger.warning(f"[FileStateManager] No state file found for agent '{agent_id}'")
            return None
        except Exception as e:
            self._logger.error(f"[FileStateManager] Failed to load state for agent '{agent_id}': {str(e)}")
            return None
    
    def delete_state(self, agent_id: str) -> bool:
        """Delete agent state file."""
        try:
            import os
            file_path = self._get_file_path(agent_id)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                self._logger.info(f"[FileStateManager] Deleted state for agent '{agent_id}'")
                return True
            else:
                self._logger.warning(f"[FileStateManager] No state file to delete for agent '{agent_id}'")
                return False
        except Exception as e:
            self._logger.error(f"[FileStateManager] Failed to delete state for agent '{agent_id}': {str(e)}")
            return False
    
    def get_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata from state file."""
        try:
            file_path = self._get_file_path(agent_id)
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return data.get('metadata')
        except Exception:
            return None
    
    def list_agents(self) -> list[str]:
        """List all agents with stored state files."""
        import os
        try:
            files = os.listdir(self._storage_dir)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except Exception as e:
            self._logger.error(f"[FileStateManager] Failed to list agents: {str(e)}")
            return []
