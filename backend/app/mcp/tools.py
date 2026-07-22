from mcp.server.fastmcp import FastMCP, Context

from app.mcp.di import AppContext
from app.mcp.errors import to_tool_error
from app.mcp.utils import log_tool_call

def register_tools(mcp: FastMCP):

    @mcp.tool()
    async def ragdocs_health(ctx: Context) -> dict:
        app_ctx: AppContext = ctx.request_context.lifespan_context

        with log_tool_call("ragdocs_health"):
            try:
                return app_ctx.health_service.check()
            except Exception as e:
                raise to_tool_error(e) from e