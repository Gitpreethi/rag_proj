from config.settings import get_settings
from rag.bm25.index import BM25Index
from rag.embeddings.sentence_transformer import get_embedding_model
from rag.reranking.reranker import Reranker
from rag.vectorstore.qdrant_store import QdrantChunkStore


def _normalize(scores: list[float]) -> list[float]:
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-9:
        return [1.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


def merge_hybrid(bm25_hits: list[dict], dense_hits: list[dict], alpha: float) -> list[dict]:
    combined: dict[str, dict] = {}
    bm25_norm = _normalize([h["score"] for h in bm25_hits])
    dense_norm = _normalize([h["score"] for h in dense_hits])

    for hit, nscore in zip(bm25_hits, bm25_norm):
        cid = hit["chunk_id"]
        combined[cid] = {**hit, "bm25_score": nscore, "dense_score": 0.0}
    for hit, nscore in zip(dense_hits, dense_norm):
        cid = hit["chunk_id"]
        if cid in combined:
            combined[cid]["dense_score"] = nscore
            combined[cid]["score"] = max(combined[cid]["score"], hit["score"])
        else:
            combined[cid] = {**hit, "bm25_score": 0.0, "dense_score": nscore}

    merged = []
    for item in combined.values():
        hybrid = alpha * item.get("dense_score", 0.0) + (1 - alpha) * item.get("bm25_score", 0.0)
        item["hybrid_score"] = hybrid
        merged.append(item)
    merged.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return merged


class HybridRetriever:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.bm25 = BM25Index()
        self.store = QdrantChunkStore()
        self.embedder = get_embedding_model()
        self.reranker = Reranker()

    def retrieve(self, query: str, filters: dict | None = None) -> list[dict]:
        bm25_hits = self.bm25.search(query, self.settings.bm25_top_k)
        qvec = self.embedder.embed_query(query)
        dense_hits = self.store.dense_search(qvec, self.settings.dense_top_k, filters=filters)
        merged = merge_hybrid(bm25_hits, dense_hits, self.settings.hybrid_alpha)
        reranked = self.reranker.rerank(query, merged, top_k=self.settings.rerank_top_k)
        return reranked
