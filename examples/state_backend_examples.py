"""
Examples: Using different state backends with AAF

This shows how to integrate AAF workflows with:
- Redis (for caching)
- PostgreSQL (for persistent state)
- Custom databases
"""

from aaf import node, workflow_graph
from aaf.state_backends import (
    RedisStateBackend,
    PostgresStateBackend,
    WorkflowStateManager
)
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


# =============================================================================
# Example 1: Redis Backend (Fast Caching)
# =============================================================================

def example_redis_backend():
    """
    Use Redis for fast, distributed state caching.
    
    Perfect for high-throughput workflows with temporary state.
    """
    print("\n" + "="*70)
    print("Example 1: Redis State Backend")
    print("="*70)
    
    # Setup Redis (requires redis-py: pip install redis)
    try:
        import redis
        
        # Connect to Redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        
        # Create Redis backend
        backend = RedisStateBackend(redis_client, prefix="aaf:demo:")
        state_mgr = WorkflowStateManager(backend)
        
        # Save workflow state with TTL
        state_mgr.save_workflow_state(
            workflow_id="order_123",
            state={
                "customer": "Alice",
                "items": ["laptop", "mouse"],
                "total": 1200.00,
                "step": "payment"
            },
            ttl=3600  # Expires in 1 hour
        )
        
        # Load state
        loaded = state_mgr.load_workflow_state("order_123")
        print(f"✓ Loaded from Redis: {loaded}")
        
        # List workflows
        workflows = state_mgr.list_workflows()
        print(f"✓ Active workflows: {workflows}")
        
        print("\n✅ Redis backend works! Great for:")
        print("  • Session state")
        print("  • Temporary caching")
        print("  • Multi-instance deployments")
        print("  • State with TTL")
        
    except ImportError:
        print("⚠️  Redis not installed. Install with: pip install redis")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}")
        print("   Make sure Redis is running on localhost:6379")


# =============================================================================
# Example 2: PostgreSQL Backend (Persistent Storage)
# =============================================================================

def example_postgres_backend():
    """
    Use PostgreSQL for persistent, reliable state storage.
    
    Perfect for production workflows that need durability.
    """
    print("\n" + "="*70)
    print("Example 2: PostgreSQL State Backend")
    print("="*70)
    
    # Setup PostgreSQL
    try:
        import psycopg2
        import os
        
        # Option 1: Use Replit's built-in database
        if 'DATABASE_URL' in os.environ:
            conn = psycopg2.connect(os.environ['DATABASE_URL'])
            print("✓ Connected to Replit PostgreSQL database")
        else:
            # Option 2: Connect to your own PostgreSQL
            conn = psycopg2.connect(
                host='localhost',
                database='aaf_db',
                user='postgres',
                password='password'
            )
            print("✓ Connected to local PostgreSQL database")
        
        # Create Postgres backend
        backend = PostgresStateBackend(conn, table_name="workflow_state")
        state_mgr = WorkflowStateManager(backend)
        
        # Save workflow state
        state_mgr.save_workflow_state(
            workflow_id="workflow_456",
            state={
                "user": "Bob",
                "action": "research",
                "results": ["finding1", "finding2"],
                "step": "analysis"
            }
        )
        
        # Load state
        loaded = state_mgr.load_workflow_state("workflow_456")
        print(f"✓ Loaded from PostgreSQL: {loaded}")
        
        # Save with TTL
        state_mgr.save_workflow_state(
            workflow_id="temp_workflow",
            state={"temp": True},
            ttl=60  # Expires in 60 seconds
        )
        
        # List workflows
        workflows = state_mgr.list_workflows()
        print(f"✓ Stored workflows: {workflows}")
        
        # Cleanup expired entries
        if hasattr(backend, 'cleanup_expired'):
            deleted = backend.cleanup_expired()
            print(f"✓ Cleaned up {deleted} expired entries")
        
        print("\n✅ PostgreSQL backend works! Great for:")
        print("  • Production workflows")
        print("  • Long-term storage")
        print("  • Audit trails")
        print("  • Complex queries")
        
        conn.close()
        
    except ImportError:
        print("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
    except Exception as e:
        print(f"⚠️  PostgreSQL connection failed: {e}")
        print("   Use Replit's database or setup local PostgreSQL")


# =============================================================================
# Example 3: State-Aware Workflow
# =============================================================================

def example_stateful_workflow():
    """
    Build a workflow that saves/loads state between executions.
    """
    print("\n" + "="*70)
    print("Example 3: Stateful Workflow")
    print("="*70)
    
    # For demo, use in-memory backend
    from aaf.state import InMemoryStateManager
    
    # Create a simple in-memory backend wrapper
    class InMemoryBackend:
        def __init__(self):
            self.store = {}
        
        def save(self, key, value, ttl=None):
            self.store[key] = value
            return True
        
        def load(self, key):
            return self.store.get(key)
        
        def delete(self, key):
            if key in self.store:
                del self.store[key]
                return True
            return False
        
        def exists(self, key):
            return key in self.store
        
        def list_keys(self, pattern="*"):
            return list(self.store.keys())
    
    backend = InMemoryBackend()
    state_mgr = WorkflowStateManager(backend)
    
    # Create stateful workflow nodes
    @node
    def load_previous_state(state):
        """Load previous workflow state if it exists."""
        workflow_id = state.get("workflow_id", "default")
        previous = state_mgr.load_workflow_state(workflow_id)
        
        if previous:
            print(f"📂 Loaded previous state: step {previous.get('step', 0)}")
            return {"previous_step": previous.get("step", 0)}
        else:
            print("📂 No previous state found, starting fresh")
            return {"previous_step": 0}
    
    @node
    def process_step(state):
        """Process current step."""
        current_step = state.get("previous_step", 0) + 1
        print(f"⚙️  Processing step {current_step}")
        return {"current_step": current_step}
    
    @node
    def save_state(state):
        """Save state for next execution."""
        workflow_id = state.get("workflow_id", "default")
        current_step = state.get("current_step", 0)
        
        state_mgr.save_workflow_state(
            workflow_id=workflow_id,
            state={"step": current_step, "data": state}
        )
        
        print(f"💾 Saved state: step {current_step}")
        return {"saved": True}
    
    @workflow_graph(
        start="load_previous_state",
        routing={
            "load_previous_state": "process_step",
            "process_step": "save_state",
            "save_state": "END"
        },
        end="END"
    )
    def stateful_workflow(workflow_id: str):
        return {"workflow_id": workflow_id}
    
    # Run workflow multiple times
    print("\n🔄 Execution 1:")
    stateful_workflow("my_workflow")
    
    print("\n🔄 Execution 2 (loads previous state):")
    stateful_workflow("my_workflow")
    
    print("\n🔄 Execution 3 (loads previous state):")
    result = stateful_workflow("my_workflow")
    
    print(f"\n✅ Workflow completed at step: {result.get('current_step')}")


# =============================================================================
# Example 4: Custom Database Backend
# =============================================================================

def example_custom_backend():
    """
    Create a custom state backend for any database.
    
    Just implement the StateBackend interface!
    """
    print("\n" + "="*70)
    print("Example 4: Custom Database Backend")
    print("="*70)
    
    from aaf.state_backends import StateBackend
    
    class MongoDBBackend(StateBackend):
        """Example: MongoDB state backend."""
        
        def __init__(self, mongo_client, db_name="aaf", collection="state"):
            self.db = mongo_client[db_name]
            self.collection = self.db[collection]
        
        def save(self, key, value, ttl=None):
            # MongoDB upsert
            self.collection.update_one(
                {"_id": key},
                {"$set": {"value": value, "updated_at": datetime.now()}},
                upsert=True
            )
            return True
        
        def load(self, key):
            doc = self.collection.find_one({"_id": key})
            return doc["value"] if doc else None
        
        def delete(self, key):
            result = self.collection.delete_one({"_id": key})
            return result.deleted_count > 0
        
        def exists(self, key):
            return self.collection.count_documents({"_id": key}) > 0
        
        def list_keys(self, pattern="*"):
            # Convert glob to regex
            import re
            regex = pattern.replace("*", ".*").replace("?", ".")
            docs = self.collection.find({"_id": {"$regex": regex}})
            return [doc["_id"] for doc in docs]
    
    print("✅ Custom backends are easy!")
    print("   Just implement: save, load, delete, exists, list_keys")
    print("\nSupported databases:")
    print("  • MongoDB")
    print("  • DynamoDB")
    print("  • Cassandra")
    print("  • Any database you want!")


# =============================================================================
# Run Examples
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("AAF State Backend Examples")
    print("="*70)
    
    # Example 1: Redis
    example_redis_backend()
    
    # Example 2: PostgreSQL
    example_postgres_backend()
    
    # Example 3: Stateful workflow
    example_stateful_workflow()
    
    # Example 4: Custom backend
    example_custom_backend()
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
AAF's state management is fully pluggable!

Choose based on your needs:
  • Redis: Fast caching, TTL, distributed
  • PostgreSQL: Persistent, reliable, queryable
  • MongoDB: Document storage, flexible schema
  • Custom: Any database you want!

Integration is simple:
  1. Create backend (Redis, Postgres, etc.)
  2. Wrap in WorkflowStateManager
  3. Use in your workflows

See examples above for code!
""")
