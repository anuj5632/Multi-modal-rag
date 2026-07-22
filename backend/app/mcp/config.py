from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class MCPSettings(BaseSettings):
    """
    MCP-only configuration, kept separate from app.core.config.Settings
    since these fields (transport, HTTP host/port, request timeout) are
    meaningless to the FastAPI process and would just be dead config
    there. Env vars are prefixed MCP_ to avoid collisions with the
    shared settings (e.g. MCP_PORT vs whatever port the FastAPI process
    binds to - those are two different servers, possibly running at once).
    """

    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")

    transport: str = "stdio"
    host: str = "localhost"
    port: int = 8000

    request_timeout_seconds: int = 30

    default_top_k: int = 5
    default_top_k_images: int = 3
    default_top_k_audio: int = 5


@lru_cache()
def get_mcp_settings() -> MCPSettings:
    return MCPSettings()

mcp_settings = get_mcp_settings()
7