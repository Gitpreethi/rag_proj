from functools import lru_cache

from config.settings import get_settings
from rag.embeddings.base import EmbeddingModel


class SentenceTransformerEmbedding(EmbeddingModel):
    """Configurable embedding backend (Qwen3-Embedding-*, BGE-M3, etc.)."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        settings = get_settings()
        self._model_name = model_name or settings.embedding_model
        self._device = device or settings.embedding_device
        self._model = None

    @property
    def model_name(self) -> str:
        return self._model_name

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name, device=self._device)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self._load()
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    return SentenceTransformerEmbedding()
