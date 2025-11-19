"""
Human-in-the-loop implementations for the Agentic Application Framework.

This module provides abstractions for human oversight, approval workflows,
and intervention points in agentic systems.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Callable
from enum import Enum


class ApprovalStatus(str, Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class InterventionPoint:
    """
    Defines a point where human intervention may be required.
    
    Used to specify when agents should pause for human review,
    approval, or modification before continuing execution.
    """
    
    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        timeout_seconds: Optional[int] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize an intervention point.
        
        Args:
            name: Unique name for this intervention point
            condition: Function that determines if intervention is needed
            timeout_seconds: Optional timeout for approval (None = no timeout)
            logger: Logger instance for debugging
        """
        self.name = name
        self.condition = condition
        self.timeout_seconds = timeout_seconds
        self._logger = logger or logging.getLogger(__name__)
    
    def should_intervene(self, context: Dict[str, Any]) -> bool:
        """
        Check if human intervention is needed.
        
        Args:
            context: Current execution context
            
        Returns:
            True if intervention is needed
        """
        try:
            result = self.condition(context)
            if result:
                self._logger.info(f"[InterventionPoint:{self.name}] Intervention required")
            return result
        except Exception as e:
            self._logger.error(f"[InterventionPoint:{self.name}] Error evaluating condition: {str(e)}")
            return False


class ApprovalWorkflow:
    """
    Manages human approval workflows for sensitive or critical operations.
    
    Allows agents to pause execution and wait for human approval before
    proceeding with high-risk actions like data deletion, financial
    transactions, or policy changes.
    """
    
    def __init__(
        self,
        approval_handler: Optional[Callable[[Dict[str, Any]], ApprovalStatus]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the approval workflow.
        
        Args:
            approval_handler: Optional custom approval handler function
            logger: Logger instance for debugging
        """
        self._logger = logger or logging.getLogger(__name__)
        self._approval_handler = approval_handler or self._default_approval_handler
        self._pending_approvals: Dict[str, Dict[str, Any]] = {}
        self._approval_history: List[Dict[str, Any]] = []
        self._logger.info("[ApprovalWorkflow] Initialized")
    
    def request_approval(
        self,
        action: str,
        context: Dict[str, Any],
        timeout_seconds: Optional[int] = 300
    ) -> ApprovalStatus:
        """
        Request human approval for an action.
        
        Args:
            action: Description of the action requiring approval
            context: Context and details about the action
            timeout_seconds: Time to wait for approval (None = wait indefinitely)
            
        Returns:
            Approval status (approved, rejected, or timeout)
        """
        request_id = f"approval_{int(time.time())}_{len(self._pending_approvals)}"
        
        approval_request = {
            "request_id": request_id,
            "action": action,
            "context": context,
            "requested_at": time.time(),
            "timeout_seconds": timeout_seconds,
            "status": ApprovalStatus.PENDING
        }
        
        self._pending_approvals[request_id] = approval_request
        self._logger.info(f"[ApprovalWorkflow] Requested approval for: {action}")
        
        status = self._approval_handler(approval_request)
        
        approval_request["status"] = status
        approval_request["resolved_at"] = time.time()
        
        self._approval_history.append(approval_request)
        self._pending_approvals.pop(request_id, None)
        
        self._logger.info(f"[ApprovalWorkflow] Approval {status.value} for: {action}")
        return status
    
    def _default_approval_handler(self, request: Dict[str, Any]) -> ApprovalStatus:
        """
        Default approval handler (auto-approves for demo purposes).
        
        In production, this should integrate with a real approval system
        (UI, email, Slack, etc.).
        """
        self._logger.warning(
            f"[ApprovalWorkflow] Using default handler - auto-approving: {request['action']}"
        )
        return ApprovalStatus.APPROVED
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """
        Get all pending approval requests.
        
        Returns:
            List of pending approval requests
        """
        return list(self._pending_approvals.values())
    
    def get_approval_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all approval requests.
        
        Returns:
            List of all approval requests with their outcomes
        """
        return self._approval_history.copy()
    
    def approve(self, request_id: str) -> bool:
        """
        Manually approve a pending request.
        
        Args:
            request_id: ID of the request to approve
            
        Returns:
            True if successfully approved
        """
        if request_id in self._pending_approvals:
            request = self._pending_approvals[request_id]
            request["status"] = ApprovalStatus.APPROVED
            request["resolved_at"] = time.time()
            
            self._approval_history.append(request)
            self._pending_approvals.pop(request_id)
            
            self._logger.info(f"[ApprovalWorkflow] Manually approved request: {request_id}")
            return True
        
        self._logger.warning(f"[ApprovalWorkflow] Request not found: {request_id}")
        return False
    
    def reject(self, request_id: str, reason: Optional[str] = None) -> bool:
        """
        Manually reject a pending request.
        
        Args:
            request_id: ID of the request to reject
            reason: Optional reason for rejection
            
        Returns:
            True if successfully rejected
        """
        if request_id in self._pending_approvals:
            request = self._pending_approvals[request_id]
            request["status"] = ApprovalStatus.REJECTED
            request["resolved_at"] = time.time()
            request["rejection_reason"] = reason
            
            self._approval_history.append(request)
            self._pending_approvals.pop(request_id)
            
            self._logger.info(f"[ApprovalWorkflow] Manually rejected request: {request_id}")
            return True
        
        self._logger.warning(f"[ApprovalWorkflow] Request not found: {request_id}")
        return False


class HumanFeedbackLoop:
    """
    Manages continuous human feedback integration into agent behavior.
    
    Enables agents to request clarification, receive corrections, and
    adapt behavior based on human guidance.
    """
    
    def __init__(
        self,
        feedback_handler: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the feedback loop.
        
        Args:
            feedback_handler: Optional custom feedback handler function
            logger: Logger instance for debugging
        """
        self._logger = logger or logging.getLogger(__name__)
        self._feedback_handler = feedback_handler or self._default_feedback_handler
        self._feedback_history: List[Dict[str, Any]] = []
        self._logger.info("[HumanFeedbackLoop] Initialized")
    
    def request_feedback(
        self,
        question: str,
        context: Dict[str, Any],
        options: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Request feedback from a human.
        
        Args:
            question: Question to ask the human
            context: Context about why feedback is needed
            options: Optional list of suggested responses
            
        Returns:
            Feedback response from human
        """
        feedback_request = {
            "request_id": f"feedback_{int(time.time())}",
            "question": question,
            "context": context,
            "options": options,
            "requested_at": time.time()
        }
        
        self._logger.info(f"[HumanFeedbackLoop] Requesting feedback: {question}")
        
        response = self._feedback_handler(question, context)
        
        feedback_request["response"] = response
        feedback_request["received_at"] = time.time()
        
        self._feedback_history.append(feedback_request)
        
        self._logger.info(f"[HumanFeedbackLoop] Received feedback response")
        return response
    
    def _default_feedback_handler(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default feedback handler (returns generic response).
        
        In production, integrate with UI, CLI prompts, or messaging systems.
        """
        self._logger.warning(
            f"[HumanFeedbackLoop] Using default handler for: {question}"
        )
        return {
            "answer": "proceed",
            "confidence": 0.5,
            "note": "Default handler - no human input received"
        }
    
    def get_feedback_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all feedback requests.
        
        Returns:
            List of all feedback interactions
        """
        return self._feedback_history.copy()


class GuardrailValidator:
    """
    Validates agent actions against safety guardrails.
    
    Prevents agents from performing dangerous or policy-violating actions.
    """
    
    def __init__(
        self,
        rules: List[Dict[str, Any]],
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the guardrail validator.
        
        Args:
            rules: List of validation rules (condition, message, severity)
            logger: Logger instance for debugging
        """
        self._logger = logger or logging.getLogger(__name__)
        self._rules = rules
        self._violations: List[Dict[str, Any]] = []
        self._logger.info(f"[GuardrailValidator] Initialized with {len(rules)} rules")
    
    def validate(self, action: Dict[str, Any]) -> bool:
        """
        Validate an action against guardrails.
        
        Args:
            action: Action to validate
            
        Returns:
            True if action passes all guardrails, False otherwise
        """
        violations = []
        
        for rule in self._rules:
            condition = rule.get("condition")
            if not condition:
                continue
            
            try:
                if condition(action):
                    violation = {
                        "rule": rule.get("name", "unnamed_rule"),
                        "message": rule.get("message", "Guardrail violation"),
                        "severity": rule.get("severity", "high"),
                        "action": action,
                        "timestamp": time.time()
                    }
                    violations.append(violation)
                    self._violations.append(violation)
                    
                    self._logger.warning(
                        f"[GuardrailValidator] Violation detected: {violation['message']}"
                    )
            except Exception as e:
                self._logger.error(f"[GuardrailValidator] Error evaluating rule: {str(e)}")
        
        return len(violations) == 0
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """
        Get all recorded violations.
        
        Returns:
            List of guardrail violations
        """
        return self._violations.copy()
    
    def clear_violations(self) -> None:
        """Clear the violation history."""
        count = len(self._violations)
        self._violations.clear()
        self._logger.info(f"[GuardrailValidator] Cleared {count} violations")
