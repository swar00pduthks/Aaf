"""
Structured logging for the Agentic Application Framework.

This module provides context-aware structured logging with automatic
metadata injection and correlation IDs for distributed tracing.
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class StructuredLogger:
    """
    Structured logger with context injection and correlation tracking.
    
    Provides structured logging with automatic context enrichment,
    correlation IDs, and JSON formatting for log aggregation systems.
    """
    
    def __init__(
        self,
        name: str,
        base_context: Optional[Dict[str, Any]] = None,
        enable_json: bool = False,
        logger: Optional[logging.Logger] = None
    ):
        self._logger = logger or logging.getLogger(name)
        self._base_context = base_context or {}
        self._enable_json = enable_json
        self._correlation_id = str(uuid.uuid4())
    
    def _enrich_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Enrich log message with context.
        
        Args:
            message: Log message
            context: Additional context to include
            
        Returns:
            Enriched message
        """
        full_context = {
            **self._base_context,
            **(context or {}),
            "correlation_id": self._correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self._enable_json:
            log_entry = {
                "message": message,
                **full_context
            }
            return json.dumps(log_entry)
        else:
            context_str = " ".join(f"{k}={v}" for k, v in full_context.items())
            return f"{message} | {context_str}"
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message with context."""
        self._logger.debug(self._enrich_message(message, context))
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log info message with context."""
        self._logger.info(self._enrich_message(message, context))
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message with context."""
        self._logger.warning(self._enrich_message(message, context))
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log error message with context."""
        self._logger.error(self._enrich_message(message, context), exc_info=exc_info)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log critical message with context."""
        self._logger.critical(self._enrich_message(message, context), exc_info=exc_info)
    
    def with_context(self, **kwargs) -> 'StructuredLogger':
        """
        Create a new logger with additional context.
        
        Args:
            **kwargs: Context key-value pairs to add
            
        Returns:
            New structured logger with merged context
        """
        new_context = {**self._base_context, **kwargs}
        return StructuredLogger(
            name=self._logger.name,
            base_context=new_context,
            enable_json=self._enable_json,
            logger=self._logger
        )
    
    def new_correlation_id(self) -> 'StructuredLogger':
        """
        Create a new logger with a fresh correlation ID.
        
        Returns:
            New structured logger with new correlation ID
        """
        new_logger = StructuredLogger(
            name=self._logger.name,
            base_context=self._base_context.copy(),
            enable_json=self._enable_json,
            logger=self._logger
        )
        new_logger._correlation_id = str(uuid.uuid4())
        return new_logger
    
    @property
    def correlation_id(self) -> str:
        """Get the current correlation ID."""
        return self._correlation_id


class LoggingContext:
    """
    Context manager for adding temporary context to structured logger.
    """
    
    def __init__(self, logger: StructuredLogger, **context):
        self._logger = logger
        self._context = context
        self._original_context = logger._base_context.copy()
    
    def __enter__(self) -> StructuredLogger:
        """Enter context and add temporary context."""
        self._logger._base_context.update(self._context)
        return self._logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original context."""
        self._logger._base_context = self._original_context
        return False
