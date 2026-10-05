import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from config.settings import get_settings
from database.models import DocumentRegistry
from database.session import SessionLocal
from rag.chunking.section_chunker import SectionAwareChunker
from rag.embeddings.sentence_transformer import get_embedding_model
from rag.parsing.extractors import extract_text
from rag.bm25.index import BM25Index
from rag.vectorstore.qdrant_store import QdrantChunkStore


def ingest_registered_documents(source_id: str | None = None, reindex: bool = False) -> dict:
    db = SessionLocal()
    store = QdrantChunkStore()
    bm25 = BM25Index()
    chunker = SectionAwareChunker()
    embedder = get_embedding_model()
    ingested = 0
    chunks_written = 0
    errors: list[str] = []

    try:
        q = db.query(DocumentRegistry)
        if source_id:
            q = q.filter_by(source_id=source_id)
        docs = q.all()
        for doc in docs:
            if not doc.local_path:
                continue
            path = Path(doc.local_path)
            if not path.exists():
                errors.append(f"Missing file: {path}")
                continue
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            if doc.checksum == checksum and not reindex:
                continue
            try:
                text, parse_meta = extract_text(path)
            except Exception as exc:
                errors.append(f"{path.name}: {exc}")
                continue
            if not text.strip():
                errors.append(f"Empty extraction: {path.name}")
                continue
            chunks = chunker.split(text)
            payloads = []
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{doc.document_id}_{idx}"
                metadata = {
                    "chunk_id": chunk_id,
                    "document_id": doc.document_id,
                    "source": doc.source_id,
                    "authority": doc.authority or "",
                    "source_type": doc.source_type or "",
                    "country": "India",
                    "state": doc.jurisdiction or "",
                    "year": doc.publication_year or "",
                    "section": chunk.section,
                    "subsection": chunk.subsection,
                    "page": chunk.page,
                    "url": doc.url or "",
                }
                payloads.append((chunk_id, chunk.text, metadata))
            vectors = embedder.embed_documents([p[1] for p in payloads])
            store.upsert_chunks(payloads, vectors)
            bm25.upsert_documents(
                [
                    {"chunk_id": cid, "text": text, "metadata": meta}
                    for cid, text, meta in payloads
                ]
            )
            doc.checksum = checksum
            doc.ingested_at = datetime.now(timezone.utc)
            ingested += 1
            chunks_written += len(payloads)
        db.commit()
    finally:
        db.close()

    return {
        "documents_ingested": ingested,
        "chunks_written": chunks_written,
        "errors": errors,
        "embedding_model": embedder.model_name,
    }
