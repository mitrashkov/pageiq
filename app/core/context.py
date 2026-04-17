import contextvars
from typing import Any, Dict, Optional

# Context variables to store request information
request_id_ctx = contextvars.ContextVar("request_id", default=None)
user_id_ctx = contextvars.ContextVar("user_id", default=None)
trace_id_ctx = contextvars.ContextVar("trace_id", default=None)

def set_request_context(request_id: Optional[str] = None, user_id: Optional[int] = None, trace_id: Optional[str] = None):
    """Set request context variables"""
    if request_id:
        request_id_ctx.set(request_id)
    if user_id:
        user_id_ctx.set(user_id)
    if trace_id:
        trace_id_ctx.set(trace_id)

def get_request_context() -> Dict[str, Any]:
    """Get current request context as a dictionary"""
    return {
        "request_id": request_id_ctx.get(),
        "user_id": user_id_ctx.get(),
        "trace_id": trace_id_ctx.get(),
    }
