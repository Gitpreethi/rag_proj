import json
from pathlib import Path

from rank_bm25 import BM25Okapi

from config.settings import get_settings


class BM25Index:
    INDEX_FILE = "bm25_corpus.json"

    def __init__(self) -> None:
        settings = get_settings()
        self.path = settings.processed_data_root / self.INDEX_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.documents: list[dict] = []
        self._bm25: BM25Okapi | None = None
        self.load()

    def load(self) -> None:
        if self.path.exists():
            self.documents = json.loads(self.path.read_text(encoding="utf-8"))
            self._rebuild()

    def save(self) -> None:
        self.path.write_text(json.dumps(self.documents, ensure_ascii=False, indent=2), encoding="utf-8")

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().split()

    def _rebuild(self) -> None:
        if not self.documents:
            self._bm25 = None
            return
        corpus = [self._tokenize(d.get("text", "")) for d in self.documents]
        self._bm25 = BM25Okapi(corpus)

    def upsert_documents(self, docs: list[dict]) -> None:
        existing = {d["chunk_id"]: d for d in self.documents}
        for doc in docs:
            existing[doc["chunk_id"]] = doc
        self.documents = list(existing.values())
        self._rebuild()
        self.save()

    def search(self, query: str, top_k: int) -> list[dict]:
        if not self._bm25:
            return []
        scores = self._bm25.get_scores(self._tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        out = []
        for idx, score in ranked:
            if score <= 0:
                continue
            doc = self.documents[idx]
            out.append(
                {
                    "chunk_id": doc["chunk_id"],
                    "text": doc.get("text", ""),
                    "score": float(score),
                    "metadata": doc.get("metadata", {}),
                }
            )
        return out
