from app.core.config import settings
from app.vectorstore.qdrant_service import client as qdrant_client
from app.cache.semantic_cache import semantic_cache


class HealthService:
    """
    Aggregates health across every backing system this app depends on.
    Used by GET /health and the ragdocs_health MCP tool - both surfaces
    should agree on what "healthy" means, so it's defined once here.
    """

    def check(self) -> dict:
        qdrant_ok = True
        qdrant_error = None

        try:
            qdrant_client.get_collections()
        except Exception as e:
            qdrant_ok = False
            qdrant_error = str(e)

        cache_status = semantic_cache.stats()
        gemini_configured = bool(settings.gemini_api_key)

        overall = "healthy" if qdrant_ok else "degraded"

        return {
            "status": overall,
            "qdrant": {"ok": qdrant_ok, "error": qdrant_error},
            "cache": cache_status,
            "gemini_configured": gemini_configured,
        }


health_service = HealthService()
