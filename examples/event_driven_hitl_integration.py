"""
Event-Driven Human-in-the-Loop Integration Examples

Shows how to integrate AAF with enterprise workflow tools using
Kafka/Redis for async approval workflows.

Integration examples:
1. Kafka-based approvals
2. Redis Pub/Sub approvals
3. Flowable workflow engine integration
4. Apache Airflow integration
5. ServiceNow integration
6. Custom UI integration
"""

import sys
sys.path.insert(0, '/home/runner/workspace')
import time
import json
from threading import Thread


# ============================================================================
# Example 1: Kafka-Based Approvals
# ============================================================================

def demo_kafka_approvals():
    """
    Show how to use Kafka for approval workflows.
    """
    print("\n" + "="*70)
    print("Example 1: Kafka-Based Human Approvals")
    print("="*70)
    
    print("""
✅ Event-Driven Approval Flow:

1. AAF workflow publishes approval request to Kafka topic
2. External system (Flowable, Airflow, custom UI) consumes request
3. Human reviews and approves/rejects in external system
4. External system publishes decision to response topic
5. AAF workflow receives decision and continues/halts

Benefits:
  • Decoupled from approval UI
  • Async processing
  • Enterprise workflow integration
  • Distributed systems support
  • Audit trail in Kafka
""")
    
    print("\nCode Example:")
    print("""
from aaf.event_driven_hitl import KafkaMessageBroker, EventDrivenHumanApproval

# Setup Kafka broker
broker = KafkaMessageBroker(
    bootstrap_servers=['localhost:9092']
)

# Create approval system
approval_system = EventDrivenHumanApproval(
    broker=broker,
    request_topic="aaf.approvals.requests",
    response_topic="aaf.approvals.responses"
)

# Request approval
decision = approval_system.request_approval(
    task_id="delete_user_123",
    task_description="Delete user account and all data",
    context={
        "user_id": "user_123",
        "requested_by": "admin@example.com",
        "reason": "GDPR right to be forgotten"
    },
    timeout=300  # 5 minutes
)

if decision["approved"]:
    print(f"Approved by {decision['approver']}")
    # Execute deletion
else:
    print(f"Rejected: {decision['reason']}")
    # Log rejection, notify requester
""")


# ============================================================================
# Example 2: Integration with AAF Workflows
# ============================================================================

def demo_aaf_workflow_integration():
    """
    Show how to integrate event-driven approvals in AAF workflows.
    """
    print("\n" + "="*70)
    print("Example 2: AAF Workflow with Event-Driven Approvals")
    print("="*70)
    
    print("""
✅ Use @requires_event_approval decorator:

from aaf import node, workflow_graph
from aaf.event_driven_hitl import (
    KafkaMessageBroker,
    requires_event_approval
)

# Setup broker
kafka_broker = KafkaMessageBroker(['localhost:9092'])

# Node requiring approval
@node
@requires_event_approval(
    broker=kafka_broker,
    task_description="Execute database migration",
    timeout=600  # 10 minutes
)
def run_migration(state):
    '''This only executes if approved via Kafka.'''
    return {"status": "migrated", "rows_affected": 1000}

# Workflow
@workflow_graph(
    start="run_migration",
    routing={"run_migration": "END"}
)
def migration_workflow():
    return {}

# Execute (will wait for Kafka approval)
result = migration_workflow()
""")


# ============================================================================
# Example 3: Flowable Integration
# ============================================================================

def demo_flowable_integration():
    """
    Show how to integrate with Flowable workflow engine.
    """
    print("\n" + "="*70)
    print("Example 3: Flowable Workflow Engine Integration")
    print("="*70)
    
    print("""
✅ Flowable listens to Kafka and creates user tasks:

1. AAF publishes approval request to Kafka
2. Flowable process engine consumes the message
3. Flowable creates a User Task for human approval
4. Human approves/rejects in Flowable UI
5. Flowable publishes decision back to Kafka
6. AAF receives decision and continues

Flowable BPMN Process:

    ┌─────────────┐
    │ Start Event │
    └──────┬──────┘
           │
    ┌──────▼────────┐
    │ Kafka Listener│ (consumes aaf.approvals.requests)
    └──────┬────────┘
           │
    ┌──────▼──────┐
    │  User Task  │  ← Human approves here
    │  "Approve?" │
    └──────┬──────┘
           │
    ┌──────▼────────┐
    │ Kafka Producer│ (publishes to aaf.approvals.responses)
    └──────┬────────┘
           │
    ┌──────▼─────┐
    │  End Event │
    └────────────┘

Flowable Service Task (Java):

public class KafkaApprovalConsumer implements JavaDelegate {
    @Override
    public void execute(DelegateExecution execution) {
        // Consume from Kafka
        String request = kafkaConsumer.poll("aaf.approvals.requests");
        
        // Create user task
        execution.setVariable("approvalRequest", request);
    }
}

public class KafkaResponseProducer implements JavaDelegate {
    @Override
    public void execute(DelegateExecution execution) {
        // Get user decision
        boolean approved = (boolean) execution.getVariable("approved");
        String reason = (String) execution.getVariable("reason");
        
        // Publish to Kafka
        kafkaProducer.send("aaf.approvals.responses", {
            "request_id": requestId,
            "approved": approved,
            "reason": reason,
            "approver": getCurrentUser()
        });
    }
}
""")


# ============================================================================
# Example 4: Apache Airflow Integration
# ============================================================================

def demo_airflow_integration():
    """
    Show how to integrate with Apache Airflow.
    """
    print("\n" + "="*70)
    print("Example 4: Apache Airflow Integration")
    print("="*70)
    
    print("""
✅ Airflow DAG for handling AAF approvals:

from airflow import DAG
from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def send_approval_email(**context):
    '''Send email to approver.'''
    request = context['ti'].xcom_pull(task_ids='consume_request')
    send_email(
        to='approvers@example.com',
        subject=f"Approval Required: {request['task_description']}",
        body=f"Request ID: {request['request_id']}\\n{request['context']}"
    )

def get_approval_decision(**context):
    '''Wait for human to click approve/reject link.'''
    # This could check a database, external API, or Slack command
    # For demo, simulating approval
    return {"approved": True, "approver": "john@example.com"}

with DAG(
    'aaf_approval_workflow',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # Triggered by Kafka
    catchup=False
) as dag:
    
    # Consume approval request from Kafka
    consume_request = ConsumeFromTopicOperator(
        task_id='consume_request',
        topics=['aaf.approvals.requests'],
        kafka_config={'bootstrap.servers': 'localhost:9092'}
    )
    
    # Send notification
    notify = PythonOperator(
        task_id='send_notification',
        python_callable=send_approval_email
    )
    
    # Wait for human decision
    wait_for_decision = PythonOperator(
        task_id='wait_for_decision',
        python_callable=get_approval_decision
    )
    
    # Publish decision to Kafka
    publish_decision = ProduceToTopicOperator(
        task_id='publish_decision',
        topic='aaf.approvals.responses',
        producer_function=lambda: context['ti'].xcom_pull(task_ids='wait_for_decision'),
        kafka_config={'bootstrap.servers': 'localhost:9092'}
    )
    
    consume_request >> notify >> wait_for_decision >> publish_decision
""")


# ============================================================================
# Example 5: ServiceNow Integration
# ============================================================================

def demo_servicenow_integration():
    """
    Show how to integrate with ServiceNow.
    """
    print("\n" + "="*70)
    print("Example 5: ServiceNow Integration")
    print("="*70)
    
    print("""
✅ ServiceNow creates Change Requests from Kafka events:

ServiceNow MID Server Script:

// Consume from Kafka
var kafkaConsumer = new KafkaConsumer('aaf.approvals.requests');

kafkaConsumer.onMessage(function(message) {
    var request = JSON.parse(message);
    
    // Create Change Request in ServiceNow
    var changeGR = new GlideRecord('change_request');
    changeGR.initialize();
    changeGR.short_description = request.task_description;
    changeGR.description = JSON.stringify(request.context);
    changeGR.u_aaf_request_id = request.request_id;  // Custom field
    changeGR.state = 'new';
    changeGR.insert();
    
    gs.info('Created Change Request: ' + changeGR.number);
});

// Business Rule: When Change Request is approved/rejected
(function executeRule(current, previous) {
    if (current.state == 'approved' || current.state == 'rejected') {
        // Publish decision to Kafka
        var kafkaProducer = new KafkaProducer('aaf.approvals.responses');
        
        kafkaProducer.send({
            request_id: current.u_aaf_request_id,
            approved: current.state == 'approved',
            approver: current.approved_by.email,
            reason: current.close_notes,
            timestamp: new GlideDateTime().toString()
        });
    }
})(current, previous);

Benefits:
  • Full ServiceNow ITIL workflow
  • Approval matrix and delegation
  • Audit trail and compliance
  • Email notifications
  • Mobile approvals via ServiceNow app
""")


# ============================================================================
# Example 6: Custom Web UI
# ============================================================================

def demo_custom_ui():
    """
    Show how to build custom approval UI.
    """
    print("\n" + "="*70)
    print("Example 6: Custom Web UI for Approvals")
    print("="*70)
    
    print("""
✅ Build a simple web UI to handle approvals:

Backend (FastAPI):

from fastapi import FastAPI, WebSocket
from aaf.event_driven_hitl import KafkaMessageBroker
import asyncio

app = FastAPI()

# Kafka broker
broker = KafkaMessageBroker(['localhost:9092'])

# Store pending approvals
pending_approvals = {}

# Background task to consume approval requests
@app.on_event("startup")
async def consume_approvals():
    def handle_request(message):
        request_id = message['request_id']
        pending_approvals[request_id] = message
        # Broadcast to all connected WebSocket clients
        broadcast_to_websockets(message)
    
    # Subscribe to requests
    thread = Thread(target=broker.subscribe,
                   args=('aaf.approvals.requests', handle_request))
    thread.daemon = True
    thread.start()

# API: Get pending approvals
@app.get("/api/approvals")
async def get_approvals():
    return list(pending_approvals.values())

# API: Approve/reject
@app.post("/api/approvals/{request_id}/decision")
async def make_decision(request_id: str, approved: bool, reason: str = ""):
    # Publish decision to Kafka
    broker.publish('aaf.approvals.responses', {
        "request_id": request_id,
        "approved": approved,
        "reason": reason,
        "approver": "current_user@example.com",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Remove from pending
    pending_approvals.pop(request_id, None)
    
    return {"status": "published"}

Frontend (React):

function ApprovalDashboard() {
    const [approvals, setApprovals] = useState([]);
    
    useEffect(() => {
        // Fetch pending approvals
        fetch('/api/approvals')
            .then(r => r.json())
            .then(setApprovals);
    }, []);
    
    const handleDecision = (requestId, approved) => {
        fetch(`/api/approvals/${requestId}/decision`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ approved })
        });
    };
    
    return (
        <div>
            <h1>Pending Approvals</h1>
            {approvals.map(approval => (
                <div key={approval.request_id}>
                    <h3>{approval.task_description}</h3>
                    <pre>{JSON.stringify(approval.context, null, 2)}</pre>
                    <button onClick={() => handleDecision(approval.request_id, true)}>
                        Approve
                    </button>
                    <button onClick={() => handleDecision(approval.request_id, false)}>
                        Reject
                    </button>
                </div>
            ))}
        </div>
    );
}
""")


# ============================================================================
# Example 7: Multi-Broker Support
# ============================================================================

def demo_multi_broker():
    """
    Show support for multiple message brokers.
    """
    print("\n" + "="*70)
    print("Example 7: Multi-Broker Support")
    print("="*70)
    
    print("""
✅ AAF supports multiple message brokers:

1. **Kafka** - Enterprise streaming platform
   from aaf.event_driven_hitl import KafkaMessageBroker
   broker = KafkaMessageBroker(['localhost:9092'])

2. **Redis Pub/Sub** - Lightweight, fast
   from aaf.event_driven_hitl import RedisMessageBroker
   import redis
   broker = RedisMessageBroker(redis.Redis())

3. **RabbitMQ** - Reliable message queue
   from aaf.event_driven_hitl import RabbitMQMessageBroker
   broker = RabbitMQMessageBroker(host='localhost')

4. **AWS SQS** - Cloud-native queue
   from aaf.event_driven_hitl import SQSMessageBroker
   broker = SQSMessageBroker(queue_url='https://...')

5. **Custom** - Implement MessageBroker interface
   class MyBroker(MessageBroker):
       def publish(self, topic, message): ...
       def subscribe(self, topic, callback): ...
       def wait_for_response(self, request_id, topic): ...

All brokers work the same way - just swap the implementation!
""")


# ============================================================================
# Main Demo
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Event-Driven Human-in-the-Loop Integration")
    print("="*70)
    print("\nIntegrate AAF approvals with enterprise workflow tools!")
    
    demo_kafka_approvals()
    demo_aaf_workflow_integration()
    demo_flowable_integration()
    demo_airflow_integration()
    demo_servicenow_integration()
    demo_custom_ui()
    demo_multi_broker()
    
    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("""
Event-Driven HITL Benefits:

✅ **Decoupled** - AAF doesn't need approval UI
✅ **Async** - Non-blocking approval workflows
✅ **Enterprise** - Integrate with existing tools
✅ **Distributed** - Works across multiple services
✅ **Auditable** - All events in message broker
✅ **Flexible** - Kafka, Redis, RabbitMQ, SQS, custom

Integration Options:

  • **Flowable** - BPMN workflow engine with user tasks
  • **Airflow** - DAG-based workflow orchestration
  • **ServiceNow** - ITIL change management
  • **Custom UI** - Build your own approval dashboard

Message Flow:

  AAF Workflow
      │
      ├─ Publish approval request → Kafka topic
      │
      ├─ External system consumes request
      │
      ├─ Human approves/rejects in external UI
      │
      ├─ External system publishes decision → Kafka topic
      │
      └─ AAF receives decision and continues

Setup:

  1. Choose message broker (Kafka, Redis, etc.)
  2. Configure request/response topics
  3. Use EventDrivenHumanApproval in workflows
  4. Build consumer in external system
  5. Publish approval decisions back to AAF

Next Steps:

  • Install broker: pip install kafka-python redis
  • See examples above for your workflow tool
  • Deploy approval consumers
  • Monitor approval metrics
""")
    print("="*70 + "\n")
