from app.embeddings.text_embedding import embedder
from app.vectorstore.qdrant_service import search_chunks

def retrieve_context(question, top_k=5):

    query_vector = embedder.embed(question)

    try:
        results = search_chunks(query_vector, top_k=top_k)
    except Exception:
        return []

    context = []

    for result in results:

        context.append({
            "score" : result.score,
            "document_id": result.payload.get("document_id", "unknown"),
            "document_name": result.payload.get("document_name", "Document"),
            "page" : result.payload["page"],
            "text" : result.payload["text"]
        })
    
    return context