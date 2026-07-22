class RAGDocsError(Exception):
    """
    Base class for all domain errors. Carries a stable `code` (for
    programmatic handling / MCP error mapping) separate from the
    human-readable `message`, and optional structured `details`.

    Both the FastAPI layer (api/*.py, mapped to HTTPException) and the
    MCP layer (mcp/errors.py, mapped to ToolError) translate these into
    their respective protocol's error shape - the business logic in
    services/ only ever needs to know about THIS exception hierarchy,
    not HTTP status codes or MCP error types.
    """

    code = "internal_error"

    def __init__self(self,message:str,*,details:dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DocumentNotFoundError(RahDocsError):
    code = "document_not_found"

class InvalidDocumentError(RAGDocsError):
    code = "invalid_document"

class FileTooLargeError(RAGDocsError):
    code = "file_too_large"

class EmbeddingError(RAGDocsError):
    code = "embedding_error"

class CacheError(RAGDocsError):
    code = "cache_error"

class GeminiError(RAGDocsError):
    code = "gemini_error"

class QdrantUnavailableError(RAGDocsError):
    code = "qdrant_unavailable"

class ValidationError(RAGDocsError):
    code = "validation_error"
