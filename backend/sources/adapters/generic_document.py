import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from database.models import DataVersion, DocumentRegistry
from sources.adapters.base import DownloadResult, ParseResult, SourceAdapter


class GenericDocumentAdapter(SourceAdapter):
    """Registers PDF/DOCX/TXT/HTML manual snapshots for RAG ingestion (Phase 5+)."""

    SUPPORTED = {".pdf", ".docx", ".txt", ".html", ".htm", ".csv", ".json"}

    def download(self) -> DownloadResult:
        return DownloadResult(
            success=False,
            skipped=True,
            message=f"{self.source.source_id}: automatic download not implemented; use manual snapshot.",
        )

    def ingest_manual_files(self, directory: Path) -> ParseResult:
        files = [p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in self.SUPPORTED]
        if not files:
            return ParseResult(success=False, message=f"No supported documents in {directory}")
        return self.parse_and_normalize(files)

    def parse_and_normalize(self, raw_files: list[Path]) -> ParseResult:
        from database.session import SessionLocal

        db = SessionLocal()
        written = 0
        try:
            for path in raw_files:
                checksum = hashlib.sha256(path.read_bytes()).hexdigest()
                document_id = f"{self.source.source_id}_{checksum[:16]}"
                existing = db.query(DocumentRegistry).filter_by(document_id=document_id).one_or_none()
                if existing and existing.checksum == checksum:
                    continue
                if existing:
                    existing.local_path = str(path)
                    existing.checksum = checksum
                    existing.ingested_at = datetime.now(timezone.utc)
                else:
                    db.add(
                        DocumentRegistry(
                            document_id=document_id,
                            source_id=self.source.source_id,
                            title=path.stem,
                            authority=self.source.authority,
                            url=self.source.url or None,
                            local_path=str(path),
                            checksum=checksum,
                            jurisdiction="India",
                            source_type="government_guideline"
                            if self.source.type == "document"
                            else "structured_snapshot",
                            ingested_at=datetime.now(timezone.utc),
                        )
                    )
                written += 1
            db.add(
                DataVersion(
                    source_id=self.source.source_id,
                    version_label=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                    checksum=hashlib.sha256(json.dumps([str(p) for p in raw_files]).encode()).hexdigest(),
                    raw_path=str(raw_files[0].parent),
                    download_timestamp=datetime.now(timezone.utc),
                    source_url=self.source.url,
                    license_notes=self.source.license_notes,
                    parse_status="registered",
                )
            )
            db.commit()
        finally:
            db.close()

        return ParseResult(
            success=True,
            message=f"Registered {written} document(s) for {self.source.source_id}",
            records_written=written,
        )
