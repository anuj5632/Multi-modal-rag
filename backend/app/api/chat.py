import os

from fastapi import APIRouter
from pydantic import BaseModel

from app.retrieval.retriever import(
    retrieve_context,
    retrieve_images,
)
from app.llm.generator import generator

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class QuestionRequest(BaseModel):
    question : str
    top_k: int = 5
    top_k_images: int = 3
    temperature: float = 0.7
    use_images: bool = True

@router.post("")
def ask_question(request: QuestionRequest):
    retrieved_chunks = retrieve_context(
        request.question,
        top_k=request.top_k,
    )

    retrieved_images = []
    if request.use_images:
        retrieved_images = retrieve_images(
            request.question,
            top_k=request.top_k_images,
        )

    answer = generator.generate_answer(
        request.question,
        retrieved_chunks,
        retrieved_images=retrieved_images,
        temperature=request.temperature,
    )

    return{
        "question" : request.question,
        "answer": answer,
        "sources":[
            {
                "document_id": chunk.get("document_id", "unknown"),
                "document_name": chunk.get("document_name", "Document"),
                "page" : chunk["page"],
                "confidence": round(
                    chunk["score"],
                    4
                ),
                "text": chunk.get("text", ""),
            }

            for chunk in retrieved_chunks
        ],
        "image_sources": [
            {
                "document_id": img.get("document_id", "unknown"),
                "document_name": img.get("document_name", "Document"),
                "page": img["page"],
                "confidence": round(img["score"], 4),
                "url": f"/static/images/{os.path.basename(img['image_path'])}",
            }
            for img in retrieved_images
        ],
    }
