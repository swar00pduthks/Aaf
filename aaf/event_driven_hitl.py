"""
Event-Driven Human-in-the-Loop (HITL) for AAF

Publishes approval requests to message brokers (Kafka, RabbitMQ, Redis)
and waits for responses from external workflow tools like Flowable,
Airflow, ServiceNow, or custom UIs.

This decouples AAF from the approval UI, enabling enterprise integrations.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MessageBroker(ABC):
    """
    Abstract message broker interface.
    
    Implementations: Kafka, RabbitMQ, Redis Pub/Sub, AWS SQS, etc.
    """
    
    @abstractmethod
    def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """Publish message to topic."""
        pass
    
    @abstractmethod
    def subscribe(
        self,
        topic: str,
        callback: Callable[[Dict[str, Any]], None],
        timeout: Optional[int] = None
    ) -> None:
        """Subscribe to topic and call callback for each message."""
        pass
    
    @abstractmethod
    def wait_for_response(
        self,
        request_id: str,
        response_topic: str,
        timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Wait for a response message matching request_id."""
        pass


class KafkaMessageBroker(MessageBroker):
    """
    Kafka-based message broker for HITL.
    
    Example:
        from kafka import KafkaProducer, KafkaConsumer
        
        broker = KafkaMessageBroker(
            bootstrap_servers=['localhost:9092']
        )
    """
    
    def __init__(self, bootstrap_servers: list, **kwargs):
        """
        Initialize Kafka broker.
        
        Args:
            bootstrap_servers: List of Kafka brokers
            **kwargs: Additional Kafka configuration
        """
        try:
            from kafka import KafkaProducer, KafkaConsumer
            
            self.bootstrap_servers = bootstrap_servers
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                **kwargs
            )
            self.kafka_consumer_class = KafkaConsumer
            self.kafka_kwargs = kwargs
            
            logger.info(f"[Kafka] Connected to {bootstrap_servers}")
            
        except ImportError:
            logger.error("kafka-python required: pip install kafka-python")
            raise
    
    def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """Publish message to Kafka topic."""
        try:
            future = self.producer.send(topic, message)
            future.get(timeout=10)  # Wait for ack
            logger.info(f"[Kafka] Published to {topic}: {message.get('request_id')}")
            
        except Exception as e:
            logger.error(f"[Kafka] Publish error: {e}")
            raise
    
    def subscribe(
        self,
        topic: str,
        callback: Callable[[Dict[str, Any]], None],
        timeout: Optional[int] = None
    ) -> None:
        """Subscribe to Kafka topic."""
        consumer = None
        try:
            consumer = self.kafka_consumer_class(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                **self.kafka_kwargs
            )
            
            logger.info(f"[Kafka] Subscribed to {topic}")
            
            start_time = time.time()
            for message in consumer:
                callback(message.value)
                
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    logger.info(f"[Kafka] Subscription timeout after {timeout}s")
                    break
                    
        except Exception as e:
            logger.error(f"[Kafka] Subscribe error: {e}")
            raise
        finally:
            if consumer:
                consumer.close()
    
    def wait_for_response(
        self,
        request_id: str,
        response_topic: str,
        timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for response message matching request_id.
        
        Args:
            request_id: Unique request ID to match
            response_topic: Topic to listen on
            timeout: Timeout in seconds
            
        Returns:
            Response message or None if timeout
        """
        logger.info(f"[Kafka] Waiting for response to {request_id}")
        
        response_container = {"data": None}
        
        def check_response(message: Dict[str, Any]):
            if message.get("request_id") == request_id:
                response_container["data"] = message
                logger.info(f"[Kafka] Received response for {request_id}")
        
        # Subscribe with timeout
        consumer = None
        try:
            consumer = self.kafka_consumer_class(
                response_topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                **self.kafka_kwargs
            )
            
            start_time = time.time()
            for message in consumer:
                check_response(message.value)
                
                if response_container["data"]:
                    break
                
                if (time.time() - start_time) > timeout:
                    logger.warning(f"[Kafka] Timeout waiting for {request_id}")
                    break
            
            return response_container["data"]
            
        except Exception as e:
            logger.error(f"[Kafka] Wait error: {e}")
            return None
        finally:
            if consumer:
                consumer.close()


class RedisMessageBroker(MessageBroker):
    """
    Redis Pub/Sub-based message broker for HITL.
    
    Example:
        import redis
        
        broker = RedisMessageBroker(
            redis_client=redis.Redis(host='localhost', port=6379)
        )
    """
    
    def __init__(self, redis_client):
        """
        Initialize Redis broker.
        
        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        logger.info("[Redis] Connected to Redis")
    
    def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """Publish message to Redis channel."""
        try:
            serialized = json.dumps(message)
            self.redis.publish(topic, serialized)
            logger.info(f"[Redis] Published to {topic}: {message.get('request_id')}")
            
        except Exception as e:
            logger.error(f"[Redis] Publish error: {e}")
            raise
    
    def subscribe(
        self,
        topic: str,
        callback: Callable[[Dict[str, Any]], None],
        timeout: Optional[int] = None
    ) -> None:
        """Subscribe to Redis channel."""
        try:
            pubsub = self.redis.pubsub()
            pubsub.subscribe(topic)
            
            logger.info(f"[Redis] Subscribed to {topic}")
            
            start_time = time.time()
            for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    callback(data)
                
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    logger.info(f"[Redis] Subscription timeout after {timeout}s")
                    break
                    
        except Exception as e:
            logger.error(f"[Redis] Subscribe error: {e}")
            raise
        finally:
            pubsub.close()
    
    def wait_for_response(
        self,
        request_id: str,
        response_topic: str,
        timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Wait for response message matching request_id."""
        logger.info(f"[Redis] Waiting for response to {request_id}")
        
        response_container = {"data": None}
        
        def check_response(message: Dict[str, Any]):
            if message.get("request_id") == request_id:
                response_container["data"] = message
                logger.info(f"[Redis] Received response for {request_id}")
        
        # Subscribe with timeout
        self.subscribe(response_topic, check_response, timeout=timeout)
        
        return response_container["data"]


class EventDrivenHumanApproval:
    """
    Event-driven human approval system.
    
    Publishes approval requests to message broker and waits for responses.
    
    Example:
        # Setup
        from kafka import KafkaProducer
        broker = KafkaMessageBroker(['localhost:9092'])
        
        approval = EventDrivenHumanApproval(
            broker=broker,
            request_topic="aaf.approvals.requests",
            response_topic="aaf.approvals.responses"
        )
        
        # Request approval
        decision = approval.request_approval(
            task_id="task_123",
            task_description="Execute SQL: DELETE FROM users WHERE...",
            context={"user": "admin", "action": "delete"}
        )
        
        if decision["approved"]:
            print("Approved!")
        else:
            print(f"Rejected: {decision['reason']}")
    """
    
    def __init__(
        self,
        broker: MessageBroker,
        request_topic: str = "aaf.approvals.requests",
        response_topic: str = "aaf.approvals.responses"
    ):
        """
        Initialize event-driven approval system.
        
        Args:
            broker: Message broker instance (Kafka, Redis, etc.)
            request_topic: Topic to publish approval requests
            response_topic: Topic to listen for responses
        """
        self.broker = broker
        self.request_topic = request_topic
        self.response_topic = response_topic
    
    def request_approval(
        self,
        task_id: str,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        required_approvers: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Request human approval for a task.
        
        Args:
            task_id: Unique task identifier
            task_description: Human-readable task description
            context: Additional context for approval decision
            timeout: Timeout in seconds
            required_approvers: List of required approver IDs/roles
            
        Returns:
            Dict with:
            - approved: bool
            - approver: str (who approved/rejected)
            - reason: str (optional rejection reason)
            - timestamp: str
        """
        request_id = str(uuid.uuid4())
        
        # Build approval request
        request = {
            "request_id": request_id,
            "task_id": task_id,
            "task_description": task_description,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
            "timeout_at": (datetime.utcnow() + timedelta(seconds=timeout)).isoformat(),
            "required_approvers": required_approvers or []
        }
        
        logger.info(f"[HITL] Requesting approval for {task_id} (request_id: {request_id})")
        
        # Publish to request topic
        self.broker.publish(self.request_topic, request)
        
        # Wait for response
        response = self.broker.wait_for_response(
            request_id=request_id,
            response_topic=self.response_topic,
            timeout=timeout
        )
        
        if not response:
            logger.warning(f"[HITL] Timeout waiting for approval of {task_id}")
            return {
                "approved": False,
                "approver": "system",
                "reason": "Timeout - no response received",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "approved": response.get("approved", False),
            "approver": response.get("approver", "unknown"),
            "reason": response.get("reason", ""),
            "timestamp": response.get("timestamp", datetime.utcnow().isoformat())
        }


# Decorator for requiring approval
def requires_event_approval(
    broker: MessageBroker,
    task_description: Optional[str] = None,
    timeout: int = 300
):
    """
    Decorator to require event-driven approval before executing function.
    
    Example:
        @requires_event_approval(
            broker=kafka_broker,
            task_description="Execute database migration"
        )
        def run_migration(state):
            # This will only run if approved
            return {"status": "migrated"}
    """
    def decorator(func):
        def wrapper(state):
            approval_system = EventDrivenHumanApproval(broker)
            
            description = task_description or f"Execute {func.__name__}"
            
            decision = approval_system.request_approval(
                task_id=func.__name__,
                task_description=description,
                context=state,
                timeout=timeout
            )
            
            if not decision["approved"]:
                logger.warning(f"[HITL] {func.__name__} rejected: {decision['reason']}")
                return {
                    **state,
                    "approved": False,
                    "rejection_reason": decision["reason"]
                }
            
            logger.info(f"[HITL] {func.__name__} approved by {decision['approver']}")
            return func(state)
        
        return wrapper
    return decorator
