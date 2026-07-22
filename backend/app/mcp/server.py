from mcp.server.fastmcp import FastMCP

from app.core.config import mcp_settings
from app.mcp.di import app_lifespan
from app.mcp.tools import register_tools
from app.core.logging import configure_logging,get_logger
from app.core.transport import get_run_kwargs

configure_logging()
logger = get_logger(__name__)

mcp = FastMCP(
    "ragdocs_mcp",
    host = mcp_settings.host,
    port = mcp_settings.port,
    lifespan = app_lifespan,
)

register_tools(mcp)

def main():
    run_kwargs = get_run_kwargs()
    logger.info(
        "mcp.starting",
        server_name = "ragdocs_mcp",
        transport = run_kwargs["transport"],
        host = mcp_settings.host,
        port = mcp.mcp_settings.port,
    )
    mcp.run(**run_kwargs)

if __name__ == "__main__":
    main()

    
