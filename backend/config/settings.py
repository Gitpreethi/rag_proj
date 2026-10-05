from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'data' / 'processed' / 'earthquake_intel.db'}"

    llm_provider: str = "openai_compatible"
    llm_model: str = "qwen3-8b"
    llm_base_url: str = ""
    llm_api_key: str = ""

    embedding_model: str = "Qwen/Qwen3-Embedding-0.6B"
    embedding_device: str = "cpu"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "india_earthquake_kb"

    hybrid_alpha: float = 0.5
    bm25_top_k: int = 20
    dense_top_k: int = 20
    rerank_top_k: int = 8
    chunk_size_tokens: int = 550
    chunk_overlap_tokens: int = 75

    reranker_model: str = "BAAI/bge-reranker-v2-m3"

    woa_bp_model_path: str = str(PROJECT_ROOT / "data" / "processed" / "models" / "woa_bp_population.joblib")
    woa_bp_training_data_path: str = ""

    ncs_events_url: str = ""
    ncs_api_key: str = ""

    prompt_version: str = "system_v1"
    random_seed: int = 42

    @property
    def source_registry_path(self) -> Path:
        return BACKEND_ROOT / "sources" / "source_registry.json"

    @property
    def raw_data_root(self) -> Path:
        return PROJECT_ROOT / "data" / "raw"

    @property
    def processed_data_root(self) -> Path:
        return PROJECT_ROOT / "data" / "processed"


@lru_cache
def get_settings() -> Settings:
    return Settings()
