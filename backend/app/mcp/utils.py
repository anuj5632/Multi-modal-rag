import time
import uuid
from contextlib import contextmanager

from fastapi import logger

from app.core.logging import get_logger

def new_request_id() -> str:
    return uuid.uuid4().hex[:12]

@contextmanager
def log_tool_call(tool_name:str, **fields):
    """
    Wraps a tools body with structured start/finish/error logs carrying a 
    request_id, tool_name, and duration_ms - the logging shape called for in the architecture doc, in one place so every 
    tool gets it for free instead of repeating boilerplate.

    Usage:
        with log_tool_call("ragdocs_ask_question",question = question):
            do the work
    """

    request_id = new_request_id()
    start = time.monotonic()

    logger.info("mcp.tool_call.start", request_id = request_id,tool_name = tool_name, **fields)
    
    try:
        yield request_id
    except Exception as e:
        duration_ms = round((time.monotonic() - start)*1000,1)
        logger.error(
            "mcp.tool_call.error",
            request_id = request_id,
            tool_name = tool_name,
            duration_ms = duration_ms,
            error_type = type(e).__name__,
            error_message = str(e),
        )
        raise
    else:
        duration_ms = round((time.monotonic() - start)*1000,1)
        logger.info(
            "mcp.tool_call.finish",
            request_id = request_id,
            tool_name = tool_name,
            duration_ms = duration_ms,
        )