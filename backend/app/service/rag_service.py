from app.retrieval.retriever import retrieve_context, retrieve_images, retrieve_audio
from app.llm.generator import generator
from app.cache.semantic_cache import semantic_cache
from app.core.exceptions import GeminiError
from app.core.logging import get_logger

logger = get_logger(__name__)


class RAGService:
    """
    Orchestrates the full ask-a-question pipeline: semantic cache check ->
    hybrid+reranked text retrieval -> image/audio retrieval -> Gemini
    generation -> cache write.

    This is the ONE place that pipeline lives. Before this refactor,
    api/chat.py had this logic inline; now api/chat.py and mcp/tools.py
    both just call RAGService.ask() and format the result for their own
    protocol. Change the pipeline once, both front doors get it.
    """

    def ask(
        self,
        question: str,
        top_k: int = 5,
        top_k_images: int = 3,
        top_k_audio: int = 5,
        use_images: bool = True,
        use_audio: bool = True,
        use_cache: bool = True,
        temperature: float = 0.7,
    ) -> dict:
        if use_cache:
            cached = semantic_cache.get(question)
            if cached:
                logger.info(
                    "rag_service.cache_hit",
                    question=question,
                    similarity=cached.get("similarity"),
                )
                return {
                    "question": question,
                    "answer": cached["answer"],
                    "sources": cached.get("sources", []),
                    "image_sources": cached.get("image_sources", []),
                    "audio_sources": cached.get("audio_sources", []),
                    "cached": True,
                    "cache_similarity": cached.get("similarity"),
                }

        retrieved_chunks = retrieve_context(question, top_k=top_k)
        retrieved_images = retrieve_images(question, top_k=top_k_images) if use_images else []
        retrieved_audio = retrieve_audio(question, top_k=top_k_audio) if use_audio else []

        try:
            answer = generator.generate_answer(
                question,
                retrieved_chunks,
                retrieved_images=retrieved_images,
                retrieved_audio=retrieved_audio,
                temperature=temperature,
            )
        except Exception as e:
            logger.error("rag_service.generation_failed", question=question, error=str(e))
            raise GeminiError(f"Answer generation failed: {e}") from e

        sources = self._format_text_sources(retrieved_chunks)
        image_sources = self._format_image_sources(retrieved_images)
        audio_sources = self._format_audio_sources(retrieved_audio)

        if use_cache:
            semantic_cache.set(
                question,
                answer,
                sources=sources,
                image_sources=image_sources,
                audio_sources=audio_sources,
            )

        logger.info(
            "rag_service.answered",
            question=question,
            num_sources=len(sources),
            num_images=len(image_sources),
            num_audio=len(audio_sources),
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "image_sources": image_sources,
            "audio_sources": audio_sources,
            "cached": False,
        }

    @staticmethod
    def _format_text_sources(retrieved_chunks):
        return [
            {
                "document_id": chunk.get("document_id", "unknown"),
                "document_name": chunk.get("document_name", "Document"),
                "page": chunk["page"],
                "confidence": round(chunk["score"], 4),
                "text": chunk.get("text", ""),
            }
            for chunk in retrieved_chunks
        ]

    @staticmethod
    def _format_image_sources(retrieved_images):
        import os

        return [
            {
                "document_id": img.get("document_id", "unknown"),
                "document_name": img.get("document_name", "Document"),
                "page": img["page"],
                "confidence": round(img["score"], 4),
                "url": f"/static/images/{os.path.basename(img['image_path'])}",
            }
            for img in retrieved_images
        ]

    @staticmethod
    def _format_audio_sources(retrieved_audio):
        import os

        return [
            {
                "document_id": clip.get("document_id", "unknown"),
                "document_name": clip.get("document_name", "Document"),
                "start_seconds": clip["start"],
                "end_seconds": clip["end"],
                "timestamp": clip["timestamp"],
                "confidence": round(clip["score"], 4),
                "text": clip.get("text", ""),
                "url": (
                    f"/static/audio/{os.path.basename(clip['file_path'])}#t={clip['start']}"
                    if clip.get("file_path") else None
                ),
            }
            for clip in retrieved_audio
        ]


rag_service = RAGService()
