import os
import json
import time
import uuid

import numpy as np

try:
    import redis
except ImportError:
    redis = None

from app.embeddings.text_embedding import embedder

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

CACHE_KEY_PREFIX = "rag:cache:"
CACHE_INDEX_KEY = "rag:cache:index"  # a Redis SET of all cache entry ids

MAX_CACHE_ENTRIES = 500
SIMILARITY_THRESHOLD = 0.92
TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days


class SemanticCache:
    """
    Caches chat answers by MEANING, not exact string match: before running
    retrieval + generation, the incoming question is embedded (BGE) and
    compared via cosine similarity against embeddings of recently cached
    questions. A close-enough match (>= SIMILARITY_THRESHOLD) short-
    circuits the entire RAG pipeline and returns the previous answer -
    skipping retrieval, reranking, and the Gemini call.

    Similarity search here is done in plain Python over entries pulled
    from Redis, since vanilla Redis (without RediSearch/RedisVL) has no
    native vector search. That's fine at this scale (capped at
    MAX_CACHE_ENTRIES); for a much larger cache, swap this for RedisVL or
    a dedicated vector cache.

    Fails open: if Redis is unreachable, caching is silently disabled and
    every request just runs the full pipeline (no crash, no cache).
    """

    def __init__(self):
        self.client = None
        self.enabled = False

        if redis is None:
            print("Semantic cache disabled: redis package not installed")
            return

        try:
            self.client = redis.from_url(REDIS_URL, decode_responses=True)
            self.client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Semantic cache disabled (Redis unavailable): {e}")
            self.client = None
            self.enabled = False

    @staticmethod
    def _cosine(a, b):
        a = np.array(a)
        b = np.array(b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def get(self, question):
        if not self.enabled:
            return None

        try:
            query_embedding = embedder.embed(question)
            entry_ids = self.client.smembers(CACHE_INDEX_KEY)

            best_entry = None
            best_score = 0.0

            for entry_id in entry_ids:
                raw = self.client.get(CACHE_KEY_PREFIX + entry_id)
                if not raw:
                    # Expired via TTL but the id lingered in the index set
                    self.client.srem(CACHE_INDEX_KEY, entry_id)
                    continue

                entry = json.loads(raw)
                score = self._cosine(query_embedding, entry["embedding"])

                if score > best_score:
                    best_score = score
                    best_entry = entry

            if best_entry and best_score >= SIMILARITY_THRESHOLD:
                best_entry["similarity"] = round(best_score, 4)
                return best_entry

            return None
        except Exception as e:
            print(f"Semantic cache read failed: {e}")
            return None

    def set(self, question, answer, sources=None, image_sources=None, audio_sources=None):
        if not self.enabled:
            return

        try:
            query_embedding = embedder.embed(question)
            entry_id = str(uuid.uuid4())

            entry = {
                "question": question,
                "embedding": query_embedding,
                "answer": answer,
                "sources": sources or [],
                "image_sources": image_sources or [],
                "audio_sources": audio_sources or [],
                "cached_at": time.time(),
            }

            self.client.set(
                CACHE_KEY_PREFIX + entry_id,
                json.dumps(entry),
                ex=TTL_SECONDS,
            )
            self.client.sadd(CACHE_INDEX_KEY, entry_id)

            self._evict_if_over_capacity()
        except Exception as e:
            print(f"Semantic cache write failed: {e}")

    def _evict_if_over_capacity(self):
        entry_ids = list(self.client.smembers(CACHE_INDEX_KEY))
        if len(entry_ids) <= MAX_CACHE_ENTRIES:
            return

        timestamps = []
        for entry_id in entry_ids:
            raw = self.client.get(CACHE_KEY_PREFIX + entry_id)
            if raw:
                timestamps.append((entry_id, json.loads(raw)["cached_at"]))

        timestamps.sort(key=lambda x: x[1])  # oldest first
        overflow = len(timestamps) - MAX_CACHE_ENTRIES

        for entry_id, _ in timestamps[:overflow]:
            self.client.delete(CACHE_KEY_PREFIX + entry_id)
            self.client.srem(CACHE_INDEX_KEY, entry_id)

    def stats(self):
        if not self.enabled:
            return {"enabled": False, "entries": 0}

        return {
            "enabled": True,
            "entries": self.client.scard(CACHE_INDEX_KEY),
            "similarity_threshold": SIMILARITY_THRESHOLD,
            "max_entries": MAX_CACHE_ENTRIES,
        }

    def clear(self):
        if not self.enabled:
            return

        entry_ids = list(self.client.smembers(CACHE_INDEX_KEY))
        for entry_id in entry_ids:
            self.client.delete(CACHE_KEY_PREFIX + entry_id)
        self.client.delete(CACHE_INDEX_KEY)


semantic_cache = SemanticCache()
