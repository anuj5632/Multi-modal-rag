import os
import re
import json
import uuid
from datetime import datetime, timezone

from app.core.config import settings
from app.core.exceptions import InvalidFileError, FileTooLargeError, DocumentNotFoundError
from app.core.logging import get_logger

from app.ingestion.pdf_loader import extract_text_from_pdf
from app.ingestion.chunker import create_chunks
from app.ingestion.image_extractor import extract_images
from app.ingestion.audio_loader import transcribe_audio
from app.ingestion.audio_chunker import create_audio_chunks
from app.embeddings.text_embedding import embedder
from app.embeddings.image_embedding import image_embedder
from app.vectorstore.qdrant_service import (
    create_collection,
    create_image_collection,
    create_audio_collection,
    insert_chunks,
    insert_images,
    insert_audio_chunks,
    delete_document_chunks,
    delete_document_images,
    delete_document_audio,
)
from app.retrieval.bm25_index import bm25_index

logger = get_logger(__name__)

METADATA_FILE = os.path.join(settings.upload_dir, "documents.json")

# Anything outside this charset gets collapsed - blocks path traversal
# (../, absolute paths) and weird filenames in one place, for every
# caller (HTTP upload AND MCP upload tool).
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_filename(filename: str) -> str:
    base = os.path.basename(filename or "")
    base = _SAFE_NAME_RE.sub("_", base)
    base = base.lstrip(".")  # no hidden files / no bare ".."
    if not base:
        raise InvalidFileError("Filename is empty or invalid after sanitization")
    return base


class DocumentService:
    """
    Owns upload, listing, metadata lookup, and deletion for both PDF and
    audio documents. This is where upload security lives centrally
    (filename sanitization, path-traversal defense, extension allowlist,
    max size) - previously implemented ad hoc inside api/upload.py, now
    guaranteed to apply identically whether a file arrives via the
    FastAPI HTTP endpoint or the MCP ragdocs_upload_document tool.
    """

    def __init__(self):
        os.makedirs(settings.upload_dir, exist_ok=True)
        os.makedirs(settings.audio_upload_dir, exist_ok=True)

    # -- persistence -------------------------------------------------

    def _load_documents(self) -> list:
        if not os.path.exists(METADATA_FILE):
            return []
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_documents(self, documents: list):
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2)

    def _check_size(self, size_bytes: int):
        max_bytes = settings.max_upload_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            raise FileTooLargeError(
                f"File exceeds max upload size of {settings.max_upload_size_mb}MB",
                details={"size_bytes": size_bytes, "max_bytes": max_bytes},
            )

    @staticmethod
    def _public(document: dict) -> dict:
        return {k: v for k, v in document.items() if k != "file_path"}

    # -- uploads -------------------------------------------------------

    def upload_pdf(self, file_bytes: bytes, filename: str) -> dict:
        safe_name = _sanitize_filename(filename)

        if not safe_name.lower().endswith(".pdf"):
            raise InvalidFileError("Only PDF files are supported")

        self._check_size(len(file_bytes))

        document_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{document_id}_{safe_name}")

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        pages = extract_text_from_pdf(file_path)
        chunks = create_chunks(pages)
        images = extract_images(file_path, document_id=document_id)

        create_collection()
        create_image_collection()

        inserted_chunks = insert_chunks(chunks, embedder, document_id, safe_name)
        bm25_index.add_chunks(inserted_chunks)
        insert_images(images, image_embedder, document_id, safe_name)

        document = {
            "id": document_id,
            "type": "pdf",
            "filename": safe_name,
            "pages": len(pages),
            "chunks": len(chunks),
            "images": len(images),
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "status": "indexed",
            "file_path": file_path,
        }

        documents = self._load_documents()
        documents.append(document)
        self._save_documents(documents)

        logger.info(
            "document_service.pdf_uploaded",
            document_id=document_id,
            filename=safe_name,
            pages=len(pages),
            chunks=len(chunks),
            images=len(images),
        )

        return self._public(document)

    def upload_audio(self, file_bytes: bytes, filename: str) -> dict:
        safe_name = _sanitize_filename(filename)

        if not safe_name.lower().endswith(settings.allowed_audio_extensions):
            raise InvalidFileError(
                f"Only audio files are supported ({', '.join(settings.allowed_audio_extensions)})"
            )

        self._check_size(len(file_bytes))

        document_id = str(uuid.uuid4())
        file_path = os.path.join(settings.audio_upload_dir, f"{document_id}_{safe_name}")

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        segments, language, duration = transcribe_audio(file_path)
        chunks = create_audio_chunks(segments)

        create_audio_collection()
        insert_audio_chunks(chunks, embedder, document_id, safe_name, file_path=file_path)

        document = {
            "id": document_id,
            "type": "audio",
            "filename": safe_name,
            "duration_seconds": round(duration, 2),
            "language": language,
            "segments": len(segments),
            "chunks": len(chunks),
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "status": "indexed",
            "file_path": file_path,
        }

        documents = self._load_documents()
        documents.append(document)
        self._save_documents(documents)

        logger.info(
            "document_service.audio_uploaded",
            document_id=document_id,
            filename=safe_name,
            duration_seconds=document["duration_seconds"],
        )

        return self._public(document)

    # -- reads -----------------------------------------------------------

    def list_documents(self) -> list:
        return [self._public(doc) for doc in self._load_documents()]

    def get_document(self, document_id: str) -> dict:
        documents = self._load_documents()
        target = next((d for d in documents if d["id"] == document_id), None)

        if not target:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        return self._public(target)

    # -- deletes ---------------------------------------------------------

    def delete_document(self, document_id: str) -> dict:
        documents = self._load_documents()
        target = next((d for d in documents if d["id"] == document_id), None)

        if not target:
            raise DocumentNotFoundError(f"Document {document_id} not found")

        delete_document_chunks(document_id)
        delete_document_images(document_id)
        delete_document_audio(document_id)
        bm25_index.remove_document(document_id)

        file_path = target.get("file_path")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        remaining = [d for d in documents if d["id"] != document_id]
        self._save_documents(remaining)

        logger.info("document_service.deleted", document_id=document_id)

        return {"message": "Document deleted", "document_id": document_id}


document_service = DocumentService()
