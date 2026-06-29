from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

import os
import shutil

from app.ingestion.pdf_loader import extract_text_from_pdf
from app.ingestion.chunker import create_chunks
from app.ingestion.image_extractor import extract_images
from app.embeddings.text_embedding import embedder
from app.vectorstore.qdrant_service import(
create_collection,
insert_chunks
)

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok = True)

@router.post("")
async def upload_documents(file: UploadFile = File(...)):

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )
    
    if file.filename.endswith(".pdf"):

        pages = extract_text_from_pdf(file_path)

        chunks = create_chunks(pages)

        images = extract_images(file_path)

        create_collection()

        insert_chunks(
            chunks,
            embedder
        )

        return{
            "message" : "PDF uploaded successfully",
            "pages" : len(pages),
            "chunks" : len(chunks),
            "images" : len(images),
            "sample_chunk" : chunks[0] if len(chunks) > 0 else None,
        }
    
    return {
        "message" : "FILE uploaded successfully",
        "path" : file_path
    }