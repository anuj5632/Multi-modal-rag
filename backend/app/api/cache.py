from fastapi import APIRouter

from app.cache.semantic_cache import semantic_cache

router = APIRouter(
    prefix="/cache",
    tags=["cache"],
)

@router.get("/stats")
def cache_stats():
    return semantic_cache.stats()

@router.delete("/clear")
def cache_clear():
    semantic_cache.clear()
    return {"message": "Cache cleared successfully."}