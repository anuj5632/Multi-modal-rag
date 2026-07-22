from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.document_service import document_service
from app.core.exceptions import (
    RAGDocsError,
    DocumentNotFoundError,
    InvalidFileError,
    FileTooLargeError,
)

router = APIRouter(
    tags=["documents"]
)

_STATUS_CODES = {
    DocumentNotFoundError: 404,
    InvalidFileError: 400,
    FileTooLargeError: 413,
}


def _http_error(e: RAGDocsError) -> HTTPException:
    status_code = _STATUS_CODES.get(type(e), 400)
    return HTTPException(status_code=status_code, detail=e.message)


@router.get("/documents")
def list_documents():
    return document_service.list_documents()


@router.get("/documents/{document_id}")
def get_document(document_id: str):
    try:
        return document_service.get_document(document_id)
    except RAGDocsError as e:
        raise _http_error(e)


@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    try:
        return document_service.delete_document(document_id)
    except RAGDocsError as e:
        raise _http_error(e)


@router.post("/upload")
async def upload_documents(file: UploadFile = File(...)):
    content = await file.read()

    try:
        document = document_service.upload_pdf(content, file.filename)
    except RAGDocsError as e:
        raise _http_error(e)

    return {
        "message": "PDF uploaded successfully",
        "pages": document["pages"],
        "chunks": document["chunks"],
        "images": document["images"],
        "document": document,
    }


@router.post("/upload/audio")
async def upload_audio(file: UploadFile = File(...)):
    content = await file.read()

    try:
        document = document_service.upload_audio(content, file.filename)
    except RAGDocsError as e:
        raise _http_error(e)

    return {
        "message": "Audio uploaded and transcribed successfully",
        "duration_seconds": document["duration_seconds"],
        "language": document["language"],
        "segments": document["segments"],
        "chunks": document["chunks"],
        "document": document,
    }
