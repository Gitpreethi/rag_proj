import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from config.settings import get_settings
from database.models import DataVersion
from database.session import SessionLocal, init_db
from rag.ingestion.document_pipeline import ingest_registered_documents
from sources.adapters.factory import get_adapter, resolve_manual_directory
from sources.registry import SourceRegistry


@dataclass
class SyncReport:
    source_id: str
    download: str
    parse: str
    records_written: int = 0
    skipped: bool = False
    errors: list[str] = field(default_factory=list)


def _latest_checksum(db, source_id: str) -> str | None:
    row = (
        db.query(DataVersion)
        .filter_by(source_id=source_id)
        .order_by(DataVersion.id.desc())
        .first()
    )
    return row.checksum if row else None


def _directory_checksum(directory: Path) -> str | None:
    if not directory.exists():
        return None
    files = sorted(p for p in directory.rglob("*") if p.is_file() and p.name != "metadata.json")
    if not files:
        return None
    h = hashlib.sha256()
    for p in files:
        h.update(p.read_bytes())
    return h.hexdigest()


def sync_source(source_id: str, force: bool = False) -> SyncReport:
    init_db()
    registry = SourceRegistry()
    source = registry.get(source_id)
    adapter = get_adapter(source)
    report = SyncReport(source_id=source_id, download="", parse="")

    manual_dir = resolve_manual_directory(source_id)
    checksum = _directory_checksum(manual_dir)

    db = SessionLocal()
    try:
        if checksum and checksum == _latest_checksum(db, source_id) and not force:
            report.skipped = True
            report.download = "unchanged"
            report.parse = "skipped (checksum match)"
            return report
    finally:
        db.close()

    dl = adapter.download()
    report.download = dl.message
    if dl.skipped and manual_dir.exists():
        parse = adapter.ingest_manual_files(manual_dir)
    elif dl.success and dl.files:
        parse = adapter.parse_and_normalize(dl.files)
    elif manual_dir.exists():
        parse = adapter.ingest_manual_files(manual_dir)
    else:
        report.parse = "no files to parse"
        return report

    report.parse = parse.message
    report.records_written = parse.records_written
    report.errors = parse.errors

    if source.type == "document":
        ingest_registered_documents(source_id=source_id)

    return report


def sync_all(force: bool = False) -> list[SyncReport]:
    registry = SourceRegistry()
    return [sync_source(s.source_id, force=force) for s in registry.list_sources()]
