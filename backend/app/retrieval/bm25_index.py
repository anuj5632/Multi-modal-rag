import os
import re
import json
import threading

from rank_bm25 import BM250kapi

STORE_DIR = "bm25_store"
STORE_PATH = os.path.join(STORE_DIR,"corpus.json")

os.makedirs(STORE_DIR, exist_ok = True)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

def _tokenize(text):
    return _TOKEN_RE.findall(text.lower())

class BM25Index:
    """
    Lightweight lexical (keyword) index over the same text chunks stored
    in Qdrant, persisted to a JSON file so it survives restarts.

    This is deliberately a from-scratch-rebuild-on-write index using
    rank_bm25 (pure Python, no server). Fine up to tens of thousands of
    chunks. For much larger corpora, swap this for Qdrant's native sparse
    vector support (FastEmbed BM25) instead of rebuilding in memory.
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.corpus = []
        self._bm25 = None
        self._load()
        self._rebuild()

    def _load(self):
        if os.path.exists(STORE_PATH):
            with open(STORE_PATH,"r",encoding = "utf-8") as f:
                self.corpus = json.load(f)
    
    def _persist(self):
        with open(STORE_PATH,"w",encoding = "utf-8") as f:
            json.dump(self.corpus,f)

    def _rebuild(self):
        if not self.corpus:
            self._bm25 = None
            return
        
        tokenized = [_tokenize(c["text"]) for c in self.corpus]
        self._bm25 = BM250kapi(tokenized)

    def add_chunks(self, chunks):
        """
        chunks: list of {id, document_id, document_name, page, text}"""
        if not chunks:
            return
        
        with self._lock:
            self.corpus.extend(chunks)
            self._persist()
            self._rebuild()
    
    def remove_document(self, document_id):
        with self._lock:
            self.corpus = [
                c for c in self.corpus if c.get("document_id") != document_id
            ]
            self._persist()
            self._rebuild()

    def search(self, query, top_k=10):
        if self._bm25 is None:
            return []

        tokens = _tokenize(query)
        if not tokens:
            return []

        scores = self._bm25.get_scores(tokens)

        ranked = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True
        )[:top_k]

        results = []
        for idx, score in ranked:
            if score <= 0:
                continue

            chunk = self.corpus[idx]
            results.append({**chunk, "bm25_score": float(score)})

        return results


bm25_index = BM25Index()

