"""
Using Replit's built-in PostgreSQL database for AAF state management.

This example shows how to use Replit's database for workflow state.
"""

import os
import logging
from aaf import node, workflow_graph
from aaf.state_backends import PostgresStateBackend, WorkflowStateManager

logging.basicConfig(level=logging.INFO, format='%(message)s')


def create_replit_state_backend():
    """
    Create a state backend using Replit's PostgreSQL database.
    
    Replit provides a free PostgreSQL database that's perfect for
    storing workflow state in production.
    """
    try:
        import psycopg2
        
        # Replit automatically provides DATABASE_URL
        if 'DATABASE_URL' not in os.environ:
            print("⚠️  Replit database not provisioned.")
            print("   Go to Tools → Database in Replit to create one.")
            return None
        
        # Connect to Replit's database
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        
        # Create backend
        backend = PostgresStateBackend(
            connection=conn,
            table_name="aaf_workflow_state"
        )
        
        state_mgr = WorkflowStateManager(backend)
        
        print("✅ Connected to Replit PostgreSQL database")
        return state_mgr
        
    except ImportError:
        print("⚠️  psycopg2 not installed")
        print("   Add to pyproject.toml: psycopg2-binary = \"*\"")
        return None
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


# Example: Workflow with persistent state
@node
def initialize_workflow(state):
    """Initialize workflow and load previous state."""
    workflow_id = state["workflow_id"]
    state_mgr = state["state_manager"]
    
    # Try to load previous state
    previous = state_mgr.load_workflow_state(workflow_id)
    
    if previous:
        print(f"📂 Resuming workflow from step {previous['current_step']}")
        return {
            "current_step": previous["current_step"],
            "data": previous.get("data", {})
        }
    else:
        print("📂 Starting new workflow")
        return {"current_step": 0, "data": {}}


@node
def process_data(state):
    """Process data and increment step."""
    current_step = state["current_step"] + 1
    
    # Simulate processing
    data = state.get("data", {})
    data[f"result_{current_step}"] = f"processed at step {current_step}"
    
    print(f"⚙️  Processing step {current_step}")
    
    return {
        "current_step": current_step,
        "data": data
    }


@node
def save_checkpoint(state):
    """Save workflow checkpoint to database."""
    workflow_id = state["workflow_id"]
    state_mgr = state["state_manager"]
    
    # Save to Replit database
    state_mgr.save_workflow_state(
        workflow_id=workflow_id,
        state={
            "current_step": state["current_step"],
            "data": state["data"]
        },
        ttl=86400  # Keep for 24 hours
    )
    
    print(f"💾 Checkpoint saved to Replit database")
    return {"checkpoint_saved": True}


@workflow_graph(
    start="initialize_workflow",
    routing={
        "initialize_workflow": "process_data",
        "process_data": "save_checkpoint",
        "save_checkpoint": "END"
    },
    end="END"
)
def persistent_workflow(workflow_id: str, state_manager: WorkflowStateManager):
    """Workflow with database-backed state."""
    return {
        "workflow_id": workflow_id,
        "state_manager": state_manager
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Replit PostgreSQL State Backend")
    print("="*70)
    
    # Create state backend
    state_mgr = create_replit_state_backend()
    
    if state_mgr:
        print("\n" + "="*70)
        print("Running Workflow with Persistent State")
        print("="*70)
        
        # Run workflow multiple times
        for i in range(1, 4):
            print(f"\n🔄 Execution {i}:")
            result = persistent_workflow("my_workflow", state_mgr)
            print(f"   Current step: {result['current_step']}")
            print(f"   Data: {result['data']}")
        
        print("\n" + "="*70)
        print("Benefits of Using Replit Database")
        print("="*70)
        print("""
✅ Free PostgreSQL database included
✅ Automatic backups and snapshots
✅ Works across workflow restarts
✅ Persistent state for production
✅ Supports rollback to previous states
✅ No configuration needed

Your workflow state survives:
  • App restarts
  • Deployments
  • Code changes
  • Replit session changes
""")
    else:
        print("\n📝 To use Replit's database:")
        print("   1. Open Tools → Database in Replit")
        print("   2. Click 'Create Database'")
        print("   3. Add psycopg2-binary to dependencies")
        print("   4. Run this script again")
