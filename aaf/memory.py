"""
Memory implementations for the Agentic Application Framework.

This module provides concrete implementations of memory systems for
agent context retention and semantic search.
"""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from aaf.abstracts import AbstractMemory, MemoryEntry


class InMemoryShortTermMemory:
    """
    Short-term memory implementation using in-memory storage.
    
    This provides fast access to recent memories with automatic cleanup
    of old entries. Suitable for conversation context and working memory.
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        max_entries: int = 100,
        ttl_seconds: Optional[int] = 3600
    ):
        """
        Initialize short-term memory.
        
        Args:
            logger: Logger instance for debugging
            max_entries: Maximum number of entries to retain
            ttl_seconds: Time-to-live for entries in seconds (None = no expiration)
        """
        self._logger = logger or logging.getLogger(__name__)
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._memories: List[MemoryEntry] = []
        self._memory_index: Dict[str, MemoryEntry] = {}
        self._logger.info(f"[ShortTermMemory] Initialized with max_entries={max_entries}, ttl={ttl_seconds}s")
    
    @property
    def memory_name(self) -> str:
        return "short_term_memory"
    
    def add(self, entry: MemoryEntry) -> bool:
        """Add a memory entry with automatic cleanup."""
        try:
            if "id" not in entry:
                entry["id"] = str(uuid.uuid4())
            
            if "metadata" not in entry:
                entry["metadata"] = {}
            
            entry["metadata"]["timestamp"] = time.time()
            entry["metadata"]["added_at"] = time.time()
            
            if "relevance_score" not in entry:
                entry["relevance_score"] = 1.0
            
            self._cleanup_old_entries()
            
            if len(self._memories) >= self._max_entries:
                oldest = self._memories.pop(0)
                self._memory_index.pop(oldest["id"], None)
                self._logger.debug(f"[ShortTermMemory] Evicted oldest entry: {oldest['id']}")
            
            self._memories.append(entry)
            self._memory_index[entry["id"]] = entry
            
            self._logger.debug(f"[ShortTermMemory] Added entry {entry['id']}: {str(entry.get('content', ''))[:50]}")
            return True
            
        except Exception as e:
            self._logger.error(f"[ShortTermMemory] Failed to add entry: {str(e)}")
            return False
    
    def search(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """
        Search for relevant memories using simple text matching.
        
        For semantic search, use VectorMemoryStore instead.
        """
        self._cleanup_old_entries()
        
        results: List[MemoryEntry] = []
        query_lower = query.lower()
        
        for memory in reversed(self._memories):
            if len(results) >= limit:
                break
            
            if metadata_filter:
                metadata_match = all(
                    memory.get("metadata", {}).get(k) == v
                    for k, v in metadata_filter.items()
                )
                if not metadata_match:
                    continue
            
            content_str = str(memory.get("content", "")).lower()
            if query_lower in content_str:
                results.append(memory.copy())
        
        self._logger.debug(f"[ShortTermMemory] Search for '{query}' found {len(results)} results")
        return results
    
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory by ID."""
        self._cleanup_old_entries()
        
        memory = self._memory_index.get(memory_id)
        if memory:
            self._logger.debug(f"[ShortTermMemory] Retrieved memory {memory_id}")
            return memory.copy()
        else:
            self._logger.debug(f"[ShortTermMemory] Memory {memory_id} not found")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        if memory_id in self._memory_index:
            memory = self._memory_index.pop(memory_id)
            self._memories.remove(memory)
            self._logger.debug(f"[ShortTermMemory] Deleted memory {memory_id}")
            return True
        else:
            self._logger.debug(f"[ShortTermMemory] Memory {memory_id} not found for deletion")
            return False
    
    def clear(self) -> bool:
        """Clear all memories."""
        count = len(self._memories)
        self._memories.clear()
        self._memory_index.clear()
        self._logger.info(f"[ShortTermMemory] Cleared {count} entries")
        return True
    
    def get_recent(self, count: int = 10) -> List[MemoryEntry]:
        """
        Get the most recent N memories.
        
        Args:
            count: Number of recent memories to retrieve
            
        Returns:
            List of recent memory entries
        """
        self._cleanup_old_entries()
        return [m.copy() for m in reversed(self._memories[-count:])]
    
    def _cleanup_old_entries(self) -> None:
        """Remove expired entries based on TTL."""
        if not self._ttl_seconds:
            return
        
        current_time = time.time()
        before_count = len(self._memories)
        
        self._memories = [
            m for m in self._memories
            if current_time - m.get("metadata", {}).get("added_at", current_time) < self._ttl_seconds
        ]
        
        self._memory_index = {m["id"]: m for m in self._memories}
        
        removed_count = before_count - len(self._memories)
        if removed_count > 0:
            self._logger.debug(f"[ShortTermMemory] Cleaned up {removed_count} expired entries")


class SimpleLongTermMemory:
    """
    Long-term memory implementation using in-memory storage.
    
    For production use, replace with vector database (Pinecone, Qdrant, etc.)
    for semantic search capabilities.
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        persistence_path: Optional[str] = None
    ):
        """
        Initialize long-term memory.
        
        Args:
            logger: Logger instance for debugging
            persistence_path: Optional path for persistent storage (future)
        """
        self._logger = logger or logging.getLogger(__name__)
        self._persistence_path = persistence_path
        self._memories: Dict[str, MemoryEntry] = {}
        self._logger.info("[LongTermMemory] Initialized")
    
    @property
    def memory_name(self) -> str:
        return "long_term_memory"
    
    def add(self, entry: MemoryEntry) -> bool:
        """Add a persistent memory entry."""
        try:
            if "id" not in entry:
                entry["id"] = str(uuid.uuid4())
            
            if "metadata" not in entry:
                entry["metadata"] = {}
            
            entry["metadata"]["timestamp"] = time.time()
            entry["metadata"]["added_at"] = time.time()
            
            if "relevance_score" not in entry:
                entry["relevance_score"] = 1.0
            
            self._memories[entry["id"]] = entry
            
            self._logger.debug(f"[LongTermMemory] Added entry {entry['id']}")
            return True
            
        except Exception as e:
            self._logger.error(f"[LongTermMemory] Failed to add entry: {str(e)}")
            return False
    
    def search(
        self,
        query: str,
        limit: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """
        Search for relevant memories using simple text matching.
        
        For semantic search, implement vector embeddings.
        """
        results: List[MemoryEntry] = []
        query_lower = query.lower()
        
        for memory in self._memories.values():
            if metadata_filter:
                metadata_match = all(
                    memory.get("metadata", {}).get(k) == v
                    for k, v in metadata_filter.items()
                )
                if not metadata_match:
                    continue
            
            content_str = str(memory.get("content", "")).lower()
            if query_lower in content_str:
                results.append(memory.copy())
        
        results.sort(key=lambda m: m.get("relevance_score", 0.0), reverse=True)
        results = results[:limit]
        
        self._logger.debug(f"[LongTermMemory] Search for '{query}' found {len(results)} results")
        return results
    
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory by ID."""
        memory = self._memories.get(memory_id)
        if memory:
            self._logger.debug(f"[LongTermMemory] Retrieved memory {memory_id}")
            return memory.copy()
        else:
            self._logger.debug(f"[LongTermMemory] Memory {memory_id} not found")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        if memory_id in self._memories:
            self._memories.pop(memory_id)
            self._logger.debug(f"[LongTermMemory] Deleted memory {memory_id}")
            return True
        else:
            self._logger.debug(f"[LongTermMemory] Memory {memory_id} not found for deletion")
            return False
    
    def clear(self) -> bool:
        """Clear all memories."""
        count = len(self._memories)
        self._memories.clear()
        self._logger.info(f"[LongTermMemory] Cleared {count} entries")
        return True
    
    def list_all(self) -> List[str]:
        """
        List all memory IDs.
        
        Returns:
            List of all memory IDs in long-term storage
        """
        return list(self._memories.keys())
