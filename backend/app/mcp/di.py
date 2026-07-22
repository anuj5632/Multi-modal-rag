from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from app.core.logging import configure_logging, get_logger
from app.services.rag_service import rag_service, RAGService
from app.services.document_service import document_service, DocumentService
from app.services.health_service import health_service, HealthService

logger = get_logger(__name__)

@dataclass
class AppContext:
    rag_service: RAGService
    document_service: DocumentService
    health_service: HealthService

@asynccontextmanager
async def app_lifespan(server:FastMCP) -> AsyncIterator[AppContext]:
    configure_logging()
    logger.info("mcp.server_starting")

    try:
        yield AppContext(
            rag_service = rag_service,
            document_service = document_service,
            health_service = health_service,
        )
    finally:
        logger.info("mcp.server_stopping")