from app.embeddings.text_embedding import embedder
from app.embeddings.image_embedding import image_embedder
from app.vectorstore.qdrant_service import search_images, search_audio_chunks
from app.ingestion.audio_chunker import format_timestamp
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.reranker import rerank


def retrieve_context(question, top_k=5, candidate_k=20, use_reranker=True):
    """
    Text retrieval pipeline: BM25 + dense hybrid search narrows the whole
    corpus down to `candidate_k` candidates via Reciprocal Rank Fusion,
    then a cross-encoder reranks those candidates for the final `top_k`
    (much more accurate than either signal alone, and cheaper than
    running the cross-encoder over the full corpus).

    use_reranker=False skips the cross-encoder pass and returns the
    fused hybrid results directly - useful if you want lower latency and
    are comfortable with slightly less precise ordering.
    """

    candidates = hybrid_search(question, top_k=candidate_k)

    if use_reranker:
        ranked = rerank(question, candidates, top_k=top_k)
        score_key = "rerank_score"
    else:
        ranked = candidates[:top_k]
        score_key = "fusion_score"

    context = []

    for item in ranked:
        context.append({
            "score": item.get(score_key, 0.0),
            "document_id": item["document_id"],
            "document_name": item["document_name"],
            "page": item["page"],
            "text": item["text"],
        })

    return context


def retrieve_images(question, top_k=3, score_threshold=0.20):
    """
    Uses CLIP to embed the question in the same space as the indexed images,
    then returns the most visually/semantically relevant ones.

    score_threshold filters out low-confidence matches, since CLIP will
    always return *something* even when no image is actually relevant.
    """

    query_vector = image_embedder.embed_text(question)

    try:
        results = search_images(query_vector, top_k=top_k)
    except Exception:
        return []

    images = []

    for result in results:
        if result.score < score_threshold:
            continue

        images.append({
            "score": result.score,
            "document_id": result.payload.get("document_id", "unknown"),
            "document_name": result.payload.get("document_name", "Document"),
            "page": result.payload["page"],
            "image_path": result.payload["image_path"],
        })

    return images


def retrieve_audio(question, top_k=5):
    """
    Searches transcribed audio chunks using the same BGE embedder as PDF
    text chunks (audio is transcribed to plain text, so no separate
    embedding model is needed here - unlike images, which need CLIP).
    """

    query_vector = embedder.embed(question)

    try:
        results = search_audio_chunks(query_vector, top_k=top_k)
    except Exception:
        return []

    audio_chunks = []

    for result in results:
        start = result.payload["start"]
        end = result.payload["end"]

        audio_chunks.append({
            "score": result.score,
            "document_id": result.payload.get("document_id", "unknown"),
            "document_name": result.payload.get("document_name", "Document"),
            "start": start,
            "end": end,
            "timestamp": f"{format_timestamp(start)}-{format_timestamp(end)}",
            "text": result.payload["text"],
            "file_path": result.payload.get("file_path"),
        })

    return audio_chunks
