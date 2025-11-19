"""
Simple demo: State management with AAF workflows

Shows how workflow state persists between executions.
"""

import sys
sys.path.insert(0, '/home/runner/workspace')

from aaf import node, workflow_graph
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


# Simple in-memory state store (for demo)
state_store = {}


@node
def load_state(state):
    """Load previous workflow state."""
    workflow_id = state["workflow_id"]
    
    if workflow_id in state_store:
        previous = state_store[workflow_id]
        print(f"📂 Loaded: Step {previous['step']}, Count: {previous['count']}")
        return {"step": previous["step"], "count": previous["count"]}
    else:
        print("📂 No previous state, starting fresh")
        return {"step": 0, "count": 0}


@node
def increment_step(state):
    """Process and increment."""
    new_step = state.get("step", 0) + 1
    new_count = state.get("count", 0) + 10
    
    print(f"⚙️  Processing: Step {new_step}, Count {new_count}")
    return {"step": new_step, "count": new_count}


@node
def save_state(state):
    """Save state for next execution."""
    workflow_id = state["workflow_id"]
    
    state_store[workflow_id] = {
        "step": state["step"],
        "count": state["count"]
    }
    
    print(f"💾 Saved: Step {state['step']}, Count {state['count']}")
    return {"saved": True}


@workflow_graph(
    start="load_state",
    routing={
        "load_state": "increment_step",
        "increment_step": "save_state",
        "save_state": "END"
    },
    end="END"
)
def stateful_workflow(workflow_id: str):
    """Workflow that remembers state between runs."""
    return {"workflow_id": workflow_id}


if __name__ == "__main__":
    print("\n" + "="*70)
    print("AAF Stateful Workflow Demo")
    print("="*70)
    print("\nThis workflow persists state between executions:\n")
    
    for i in range(1, 5):
        print(f"🔄 Execution {i}:")
        result = stateful_workflow("demo_workflow")
        print(f"   Result: Step {result['step']}, Count {result['count']}\n")
    
    print("="*70)
    print("✅ State persisted across 4 executions!")
    print("\nIn production, replace state_store dict with:")
    print("  • Redis (fast caching)")
    print("  • PostgreSQL (Replit database)")
    print("  • MongoDB (document storage)")
    print("  • Any database you want!")
    print("="*70 + "\n")
