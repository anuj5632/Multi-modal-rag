from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model = None

def _load_model():
    global _model
    if _model is None:
        print(f"loading reranker model {MODEL_NAME}")
        _model = CrossEncoder(MODEL_NAME)
        print("Reranker loaded")
    return _model

def rerank(question,candidates, top_k = 5):
    if not candidates:
        return []
    
    model = _load_model()

    pairs = [(question, c["text"]) for c in candidates]
    scores = model.predict(pairs)

    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)

    ranked = sorted(candidates,key = lambda c: c["rerank_score"],reverse = True)

    return ranked[:top_k]