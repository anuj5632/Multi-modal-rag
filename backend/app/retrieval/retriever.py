from app.embeddings.text_embedding import embedder
from app.vectorstore.qdrant_service import search_chunks

def retrieve_context(question):

    query_vector = embedder.embed(question)

    results = search_chunks(query_vector)

    context = []

    for result in results:

        context.append({
            "score" : result.score,
            "page" : result.payload["page"],
            "text" : result.payload["text"]
        })
    
    return context