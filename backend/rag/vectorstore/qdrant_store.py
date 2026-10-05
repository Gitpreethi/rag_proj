from typing import Any

from config.settings import get_settings


class QdrantChunkStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.collection = settings.qdrant_collection
        self.url = settings.qdrant_url
        self.api_key = settings.qdrant_api_key or None
        self._client = None
        self._memory_fallback: dict[str, dict[str, Any]] = {}

    def _client_or_none(self):
        if self._client is not None:
            return self._client
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http.models import Distance, VectorParams

            self._client = QdrantClient(path="./qdrant_storage")
            return self._client
        except Exception:
            return None

    def _ensure_collection(self, vector_size: int) -> None:
        client = self._client_or_none()
        if client is None:
            return
        from qdrant_client.http.models import Distance, VectorParams

        if not client.collection_exists(self.collection):
            client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert_chunks(self, payloads: list[tuple[str, str, dict]], vectors: list[list[float]]) -> None:
        if vectors:
            self._ensure_collection(len(vectors[0]))
        client = self._client_or_none()
        if client is None:
            for (chunk_id, text, meta), vector in zip(payloads, vectors):
                self._memory_fallback[chunk_id] = {"text": text, "meta": meta, "vector": vector}
            return
        from qdrant_client.http.models import PointStruct

        points = [
            PointStruct(
                id=abs(hash(chunk_id)) % (10**12),
                vector=vector,
                payload={**meta, "chunk_text": text},
            )
            for (chunk_id, text, meta), vector in zip(payloads, vectors)
        ]
        client.upsert(collection_name=self.collection, points=points)

    def dense_search(self,query_vector: list[float],top_k: int,filters: dict | None = None,) -> list[dict]:

        client = self._client_or_none()
    
        # If Qdrant is unavailable, use the in-memory fallback
        if client is None:
            return self._memory_search(
                query_vector,
                top_k,
                filters,
            )
    
        from qdrant_client.http.models import (
            FieldCondition,
            Filter,
            MatchValue,
        )
    
        # Build Qdrant filter
        qfilter = None
    
        if filters:
            conditions = [
                FieldCondition(
                    key=k,
                    match=MatchValue(value=v),
                )
                for k, v in filters.items()
                if v
            ]
    
            if conditions:
                qfilter = Filter(must=conditions)
    
        # New Qdrant API
        result = client.query_points(
            collection_name=self.collection,
            query=query_vector,
            limit=top_k,
            query_filter=qfilter,
        )
    
        # Convert Qdrant results into the format expected by the RAG retriever
        results = []
    
        for hit in result.points:
            payload = hit.payload or {}
    
            results.append(
                {
                    "chunk_id": payload.get("chunk_id"),
                    "text": payload.get("chunk_text", ""),
                    "score": float(hit.score),
                    "metadata": payload,
                }
            )
    
        return results

    def _memory_search(self, query_vector: list[float], top_k: int, filters: dict | None = None) -> list[dict]:
        import math

        def dot(a, b):
            return sum(x * y for x, y in zip(a, b))

        def norm(a):
            return math.sqrt(sum(x * x for x in a))

        scored = []
        for chunk_id, item in self._memory_fallback.items():
            meta = item["meta"]
            if filters:
                if any(meta.get(k) != v for k, v in filters.items() if v):
                    continue
            score = dot(query_vector, item["vector"]) / (norm(query_vector) * norm(item["vector"]) + 1e-9)
            scored.append(
                {
                    "chunk_id": chunk_id,
                    "text": item["text"],
                    "score": score,
                    "metadata": meta,
                }
            )
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
