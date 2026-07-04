from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

import os
import shutil
import uuid
import json
from datetime import datetime, timezone

from app.ingestion.pdf_loader import extract_text_from_pdf
from app.ingestion.chunker import create_chunks
from app.ingestion.image_extractor import extract_images
from app.embeddings.text_embedding import embedder
from app.embeddings.image_embedding import image_embedder
from app.vectorstore.qdrant_service import(
create_collection,
create_image_collection,
insert_chunks,
insert_images,
delete_document_chunks,
delete_document_images,
)

router = APIRouter(
    tags=["documents"]
)

UPLOAD_DIR = "uploads"
METADATA_FILE = os.path.join(UPLOAD_DIR, "documents.json")

os.makedirs(UPLOAD_DIR, exist_ok = True)


def _load_documents():
    if not os.path.exists(METADATA_FILE):
        return []

    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_documents(documents):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2)


@router.get("/documents")
def list_documents():
    return _load_documents()


@router.delete("/documents/{document_id}")
def delete_document(document_id: str):
    documents = _load_documents()
    target = next((doc for doc in documents if doc["id"] == document_id), None)

    if not target:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_document_chunks(document_id)
    delete_document_images(document_id)

    file_path = target.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    remaining_documents = [doc for doc in documents if doc["id"] != document_id]
    _save_documents(remaining_documents)
    return {"message": "Document deleted"}

@router.post("/upload")
async def upload_documents(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    document_id = str(uuid.uuid4())
    saved_name = f"{document_id}_{file.filename}"

    file_path = os.path.join(
        UPLOAD_DIR,
        saved_name
    )

    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    pages = extract_text_from_pdf(file_path)

    chunks = create_chunks(pages)

    images = extract_images(file_path, document_id=document_id)

    create_collection()
    create_image_collection()

    insert_chunks(
        chunks,
        embedder,
        document_id,
        file.filename,
    )

    insert_images(
        images,
        image_embedder,
        document_id,
        file.filename,
    )

    document = {
        "id": document_id,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "images": len(images),
        "upload_time": datetime.now(timezone.utc).isoformat(),
        "status": "indexed",
        "file_path": file_path,
    }

    documents = _load_documents()
    documents.append(document)
    _save_documents(documents)

    response_document = dict(document)
    response_document.pop("file_path", None)

    return{
        "message" : "PDF uploaded successfully",
        "pages" : len(pages),
        "chunks" : len(chunks),
        "images" : len(images),
        "document": response_document,
    }
