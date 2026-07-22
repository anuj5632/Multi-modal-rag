from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Single source of truth for configuration, shared by both the FastAPI
    API layer and the MCP server. Previously these values were scattered
    as individual os.getenv() calls across main.py, generator.py,
    semantic_cache.py, and upload.py - collecting them here means both
    "front doors" (HTTP and MCP) are guaranteed to agree on config, and
    there's one place to look when tuning defaults.
    """

    model_config = SettingsConfigDict(env_file = ".env",extra = "ignore")

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    redis_url:str = "redis://localhost:6379/0"

    upload_dir: str = "uploads"
    audio_dir: str = "audio_uploads"
    image_dir:str = "extracted_images"

    max_uploads_size_mb: int = 5
    allowed_audio_extensions: tuple[str, ...] = (".mp3", ".wav", ".ogg",".flac",".m4a")

    default_top_k: int = 5
    default_top_k_images: int = 3
    default_top_k_audio: int = 5

    frontend_url: str = "http://localhost:3000"

    log_level: str = "INFO"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

