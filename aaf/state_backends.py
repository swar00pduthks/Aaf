"""
Pluggable state backends for AAF - Redis, PostgreSQL, MongoDB, etc.

AAF's state management is fully pluggable. You can use any backend:
- Redis (for fast caching)
- PostgreSQL (for persistent state)
- MongoDB (for document storage)
- Custom databases (just implement the interface)
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod


class StateBackend(ABC):
    """
    Abstract base for state backends.
    
    Implement this interface to create custom state backends.
    """
    
    @abstractmethod
    def save(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Save state with optional TTL (time-to-live in seconds)."""
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load state by key."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete state by key."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
    
    @abstractmethod
    def list_keys(self, pattern: str = "*") -> list[str]:
        """List all keys matching pattern."""
        pass


class RedisStateBackend(StateBackend):
    """
    Redis backend for fast, distributed state caching.
    
    Perfect for:
    - High-throughput workflows
    - Multi-instance deployments
    - Temporary/session state
    - State that needs TTL
    
    Example:
        import redis
        
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        
        backend = RedisStateBackend(redis_client)
        backend.save("workflow_123", {"step": 1}, ttl=3600)  # 1 hour TTL
    """
    
    def __init__(self, redis_client, prefix: str = "aaf:state:", logger: Optional[logging.Logger] = None):
        """
        Initialize Redis backend.
        
        Args:
            redis_client: Redis client instance (from redis-py)
            prefix: Key prefix for namespacing (default: "aaf:state:")
            logger: Optional logger
        """
        self.redis = redis_client
        self.prefix = prefix
        self.logger = logger or logging.getLogger(__name__)
    
    def _make_key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}{key}"
    
    def save(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Save state to Redis.
        
        Args:
            key: State key
            value: State data (will be JSON-serialized)
            ttl: Time-to-live in seconds (optional)
        """
        try:
            redis_key = self._make_key(key)
            serialized = json.dumps(value)
            
            if ttl:
                self.redis.setex(redis_key, ttl, serialized)
                self.logger.info(f"[Redis] Saved {key} with TTL {ttl}s")
            else:
                self.redis.set(redis_key, serialized)
                self.logger.info(f"[Redis] Saved {key}")
            
            return True
        except Exception as e:
            self.logger.error(f"[Redis] Save failed for {key}: {e}")
            return False
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load state from Redis."""
        try:
            redis_key = self._make_key(key)
            value = self.redis.get(redis_key)
            
            if value:
                self.logger.info(f"[Redis] Loaded {key}")
                return json.loads(value)
            else:
                self.logger.warning(f"[Redis] Key not found: {key}")
                return None
        except Exception as e:
            self.logger.error(f"[Redis] Load failed for {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete state from Redis."""
        try:
            redis_key = self._make_key(key)
            result = self.redis.delete(redis_key)
            self.logger.info(f"[Redis] Deleted {key}")
            return result > 0
        except Exception as e:
            self.logger.error(f"[Redis] Delete failed for {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        redis_key = self._make_key(key)
        return self.redis.exists(redis_key) > 0
    
    def list_keys(self, pattern: str = "*") -> list[str]:
        """List keys matching pattern."""
        redis_pattern = f"{self.prefix}{pattern}"
        keys = self.redis.keys(redis_pattern)
        # Remove prefix from keys
        return [k.replace(self.prefix, "") for k in keys]


class PostgresStateBackend(StateBackend):
    """
    PostgreSQL backend for persistent, reliable state storage.
    
    Perfect for:
    - Production workflows
    - Long-term state retention
    - Audit trails
    - Complex queries on state
    
    Example:
        import psycopg2
        
        conn = psycopg2.connect(
            host="localhost",
            database="aaf_db",
            user="user",
            password="password"
        )
        
        backend = PostgresStateBackend(conn)
        backend.save("workflow_123", {"step": 1})
    
    Or use Replit's built-in database:
        import os
        import psycopg2
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        backend = PostgresStateBackend(conn)
    """
    
    def __init__(
        self,
        connection,
        table_name: str = "aaf_workflow_state",
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize PostgreSQL backend.
        
        Args:
            connection: psycopg2 connection object
            table_name: Table name for state storage
            logger: Optional logger
        """
        self.conn = connection
        self.table_name = table_name
        self.logger = logger or logging.getLogger(__name__)
        self._create_table()
    
    def _create_table(self):
        """Create state table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key VARCHAR(255) PRIMARY KEY,
                    value JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ttl TIMESTAMP NULL
                )
            """)
            
            # Create index for TTL cleanup
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_{self.table_name}_ttl
                ON {self.table_name} (ttl)
                WHERE ttl IS NOT NULL
            """)
            
            self.conn.commit()
            cursor.close()
            self.logger.info(f"[Postgres] Table {self.table_name} ready")
        except Exception as e:
            self.logger.error(f"[Postgres] Table creation failed: {e}")
            self.conn.rollback()
    
    def save(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Save state to PostgreSQL.
        
        Args:
            key: State key
            value: State data (stored as JSONB)
            ttl: Time-to-live in seconds (optional)
        """
        try:
            cursor = self.conn.cursor()
            
            # Calculate TTL timestamp
            ttl_timestamp = None
            if ttl:
                ttl_timestamp = f"NOW() + INTERVAL '{ttl} seconds'"
            
            # Upsert (INSERT or UPDATE)
            if ttl_timestamp:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} (key, value, ttl, updated_at)
                    VALUES (%s, %s, {ttl_timestamp}, CURRENT_TIMESTAMP)
                    ON CONFLICT (key)
                    DO UPDATE SET
                        value = EXCLUDED.value,
                        ttl = EXCLUDED.ttl,
                        updated_at = CURRENT_TIMESTAMP
                """, (key, json.dumps(value)))
            else:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} (key, value, updated_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (key)
                    DO UPDATE SET
                        value = EXCLUDED.value,
                        updated_at = CURRENT_TIMESTAMP
                """, (key, json.dumps(value)))
            
            self.conn.commit()
            cursor.close()
            self.logger.info(f"[Postgres] Saved {key}")
            return True
        except Exception as e:
            self.logger.error(f"[Postgres] Save failed for {key}: {e}")
            self.conn.rollback()
            return False
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load state from PostgreSQL."""
        try:
            cursor = self.conn.cursor()
            
            # Load and check TTL
            cursor.execute(f"""
                SELECT value FROM {self.table_name}
                WHERE key = %s
                AND (ttl IS NULL OR ttl > NOW())
            """, (key,))
            
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                self.logger.info(f"[Postgres] Loaded {key}")
                return row[0]  # JSONB is automatically deserialized
            else:
                self.logger.warning(f"[Postgres] Key not found or expired: {key}")
                return None
        except Exception as e:
            self.logger.error(f"[Postgres] Load failed for {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete state from PostgreSQL."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE key = %s", (key,))
            self.conn.commit()
            deleted = cursor.rowcount > 0
            cursor.close()
            
            if deleted:
                self.logger.info(f"[Postgres] Deleted {key}")
            return deleted
        except Exception as e:
            self.logger.error(f"[Postgres] Delete failed for {key}: {e}")
            self.conn.rollback()
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in PostgreSQL."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                SELECT 1 FROM {self.table_name}
                WHERE key = %s
                AND (ttl IS NULL OR ttl > NOW())
            """, (key,))
            exists = cursor.fetchone() is not None
            cursor.close()
            return exists
        except Exception as e:
            self.logger.error(f"[Postgres] Exists check failed for {key}: {e}")
            return False
    
    def list_keys(self, pattern: str = "*") -> list[str]:
        """List keys matching pattern (SQL LIKE syntax)."""
        try:
            cursor = self.conn.cursor()
            
            # Convert glob pattern to SQL LIKE pattern
            like_pattern = pattern.replace("*", "%").replace("?", "_")
            
            cursor.execute(f"""
                SELECT key FROM {self.table_name}
                WHERE key LIKE %s
                AND (ttl IS NULL OR ttl > NOW())
            """, (like_pattern,))
            
            keys = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return keys
        except Exception as e:
            self.logger.error(f"[Postgres] List keys failed: {e}")
            return []
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired state (TTL expired).
        
        Returns:
            Number of expired entries deleted
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"""
                DELETE FROM {self.table_name}
                WHERE ttl IS NOT NULL AND ttl < NOW()
            """)
            self.conn.commit()
            deleted = cursor.rowcount
            cursor.close()
            
            if deleted > 0:
                self.logger.info(f"[Postgres] Cleaned up {deleted} expired entries")
            return deleted
        except Exception as e:
            self.logger.error(f"[Postgres] Cleanup failed: {e}")
            self.conn.rollback()
            return 0


class WorkflowStateManager:
    """
    High-level state manager for workflows.
    
    Wraps any StateBackend and provides workflow-specific functionality.
    
    Example:
        # Use Redis
        import redis
        redis_client = redis.Redis()
        backend = RedisStateBackend(redis_client)
        state_mgr = WorkflowStateManager(backend)
        
        # Use PostgreSQL
        import psycopg2
        conn = psycopg2.connect(...)
        backend = PostgresStateBackend(conn)
        state_mgr = WorkflowStateManager(backend)
        
        # Use in workflow
        @workflow_graph(...)
        def my_workflow(data):
            state_mgr.save("workflow_123", {"current_step": 1})
            return {"data": data}
    """
    
    def __init__(self, backend: StateBackend, logger: Optional[logging.Logger] = None):
        """
        Initialize state manager with a backend.
        
        Args:
            backend: StateBackend implementation (Redis, Postgres, etc.)
            logger: Optional logger
        """
        self.backend = backend
        self.logger = logger or logging.getLogger(__name__)
    
    def save_workflow_state(
        self,
        workflow_id: str,
        state: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Save workflow state."""
        return self.backend.save(f"workflow:{workflow_id}", state, ttl)
    
    def load_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state."""
        return self.backend.load(f"workflow:{workflow_id}")
    
    def save_node_state(
        self,
        workflow_id: str,
        node_id: str,
        state: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """Save individual node state."""
        return self.backend.save(f"node:{workflow_id}:{node_id}", state, ttl)
    
    def load_node_state(self, workflow_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """Load individual node state."""
        return self.backend.load(f"node:{workflow_id}:{node_id}")
    
    def list_workflows(self) -> list[str]:
        """List all workflow IDs."""
        keys = self.backend.list_keys("workflow:*")
        return [k.replace("workflow:", "") for k in keys]
