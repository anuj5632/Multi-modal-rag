import os

from fastapi import APIRouter
from pydantic import BaseModel

from app.retrieval.retriever import(
    retrieve_context,
    retrieve_images,
    retrieve_audio,
)
from app.llm.generator import generator
from app.cache.semantic_cache import semantic_cache

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class QuestionRequest(BaseModel):
    question : str
    top_k: int = 5
    top_k_images: int = 3
    top_k_audio: int = 5
    temperature: float = 0.7
    use_images: bool = True
    use_audio: bool = True
    use_cache: bool = True

@router.post("")
def ask_question(request: QuestionRequest):
    return rag_service.ask(
        question = request.question,
        top_k = request.top_k,
        top_k_images = request.top_k_images,
        top_k_audio = request.top_k_audio,
        use_images = request.use_images,
        use_audio = request.use_audio,
        use_cache = request.use_cache,
        temperature = request.temperature,
    )

    # if request.use_cache:
    #     cached = semantic_cache.get(request.question)
    #     if cached:
    #         return {
    #             "question": request.question,
    #             "answer": cached["answer"],
    #             "sources": cached.get("sources", []),
    #             "image_sources": cached.get("image_sources", []),
    #             "audio_sources": cached.get("audio_sources", []),
    #             "cached": True,
    #             "cache_similarity": cached.get("similarity"),
    #         }

    # retrieved_chunks = retrieve_context(
    #     request.question,
    #     top_k=request.top_k,
    # )

    # retrieved_images = []
    # if request.use_images:
    #     retrieved_images = retrieve_images(
    #         request.question,
    #         top_k=request.top_k_images,
    #     )

    # retrieved_audio = []
    # if request.use_audio:
    #     retrieved_audio = retrieve_audio(
    #         request.question,
    #         top_k=request.top_k_audio,
    #     )

    # answer = generator.generate_answer(
    #     request.question,
    #     retrieved_chunks,
    #     retrieved_images=retrieved_images,
    #     retrieved_audio=retrieved_audio,
    #     temperature=request.temperature,
    # )

    # sources = [
    #     {
    #         "document_id": chunk.get("document_id", "unknown"),
    #         "document_name": chunk.get("document_name", "Document"),
    #         "page" : chunk["page"],
    #         "confidence": round(
    #             chunk["score"],
    #             4
    #         ),
    #         "text": chunk.get("text", ""),
    #     }

    #     for chunk in retrieved_chunks
    # ]

    # image_sources = [
    #     {
    #         "document_id": img.get("document_id", "unknown"),
    #         "document_name": img.get("document_name", "Document"),
    #         "page": img["page"],
    #         "confidence": round(img["score"], 4),
    #         "url": f"/static/images/{os.path.basename(img['image_path'])}",
    #     }
    #     for img in retrieved_images
    # ]

    # audio_sources = [
    #     {
    #         "document_id": clip.get("document_id", "unknown"),
    #         "document_name": clip.get("document_name", "Document"),
    #         "start_seconds": clip["start"],
    #         "end_seconds": clip["end"],
    #         "timestamp": clip["timestamp"],
    #         "confidence": round(clip["score"], 4),
    #         "text": clip.get("text", ""),
    #         "url": (
    #             f"/static/audio/{os.path.basename(clip['file_path'])}#t={clip['start']}"
    #             if clip.get("file_path") else None
    #         ),
    #     }
    #     for clip in retrieved_audio
    # ]

    # if request.use_cache:
    #     semantic_cache.set(
    #         request.question,
    #         answer,
    #         sources=sources,
    #         image_sources=image_sources,
    #         audio_sources=audio_sources,
    #     )

    # return{
    #     "question" : request.question,
    #     "answer": answer,
    #     "sources": sources,
    #     "image_sources": image_sources,
    #     "audio_sources": audio_sources,
    #     "cached": False,
    # }
