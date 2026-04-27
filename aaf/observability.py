import time
import functools
import logging
import inspect
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

def instrument(name: Optional[str] = None) -> Callable:
    """
    A decorator for instrumenting AAF agents and workflows.
    In a full production setup, this hooks into OpenTelemetry.
    Currently, it logs execution traces and durations to the standard logger.
    """
    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            logger.info(f"[TRACE START] {span_name} - args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"[TRACE END] {span_name} - duration: {duration:.4f}s - status: SUCCESS")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[TRACE ERROR] {span_name} - duration: {duration:.4f}s - exception: {e}")
                raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            logger.info(f"[TRACE START] {span_name} - args: {args}, kwargs: {kwargs}")
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"[TRACE END] {span_name} - duration: {duration:.4f}s - status: SUCCESS")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[TRACE ERROR] {span_name} - duration: {duration:.4f}s - exception: {e}")
                raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
