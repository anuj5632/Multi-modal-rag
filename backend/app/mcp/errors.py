from mcp.server.fastmcp.exceptions import ToolError
from app.core.exceptions import RAGDocsError
from app.core.logging import get_logger

logger = get_logger(__name__)

def to_tool_error(e:Exception) -> ToolError:
    if isinstance(e, RAGDocsError):
        return ToolError(f"[{e.code}] {e.message}")
    
    logger.error("mcp.unhandled_exception", error = str(e),error_type = type(e).name)
    return ToolError(f"[internal_error] {str(e)}")