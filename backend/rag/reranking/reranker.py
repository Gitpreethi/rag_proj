from config.settings import get_settings


class Reranker:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_name = settings.reranker_model
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name)
            except Exception:
                self._model = False

    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        if not candidates:
            return []
        self._load()
        if self._model is False:
            return candidates[:top_k]
        pairs = [(query, c.get("text", "")) for c in candidates]
        scores = self._model.predict(pairs)
        for cand, score in zip(candidates, scores):
            cand["rerank_score"] = float(score)
        candidates.sort(key=lambda x: x.get("rerank_score", 0.0), reverse=True)
        return candidates[:top_k]
