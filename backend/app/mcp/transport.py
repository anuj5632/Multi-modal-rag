from app.mcp.config import mcp_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

VALID_TRANSPORTS = ("stdio","streamable","http")

def get_run_kwargs():

    transport = mcp.settings.transport

    if transport not in VALID_TRANSPORTS:
        logger.warning(
            "mcp.invalid_transport_falling_back_to_stdio",
            requested=transport,
            valid=VALID_TRANSPORTS,
        )
        transport = "stdio"

    return {"transport": transport}
        

        
    