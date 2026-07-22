from app.embeddings.text_embedding import embedder
from app.vectorstore.qdrant_service import search_chunks
from app.retrieval.bm25_index import bm25_index

RRF_K = 60

def _dense_results(question, top_k):
    query_vector = embedder.embed(question)

    try:
        results = search_chunks(query_vector, top_k = top_k)
    
    except Exception:
        return []
    
    return [
        {
            "id":str(r.id),
            "document_id":r.payload.get("document_id","unknown"),
            "document_name":r.payload.get("document_name","Document"),
            "page":r.payload["page"],
            "text":r.payload["text"],
            "dense_score":r.score,
        }
        for r in results
    ]

def _bm25_results(question,top_k):
    return bm25_index.search(question,top_k = top_k)

def hybrid_search(question, top_k = 10,dense_k = 20,bm25_k = 20):
    dense = _dense_results(question,dense_k)
    lexical = _bm25_results(question,bm25_k)

    scores = {}
    payloads = {}

    for rank, item in enumerate(dense):
        key = item["id"]
        scores[key] = scores.get(key,0.0) + 1.0 / (RRF_K + rank + 1)
        payloads[key] = item

    for rank, item in enumerate(lexical):
        key = item["id"]
        scores[key] = scores.get(key,0.0) + 1.0 / (RRF_K + rank + 1)
        payloads.setdefault(key,item)

    fused = sorted(scores.items(),key = lambda x : x[1],reverse = True)[:top_k]

    return [
        {**payloads[key], " fusion_score":score}
        for key, score in fused
    ]
