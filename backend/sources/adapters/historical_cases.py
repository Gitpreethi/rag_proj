import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from database.models import DataVersion, HistoricalCase, HistoricalResource
from sources.adapters.base import DownloadResult, ParseResult, SourceAdapter


class HistoricalCasesAdapter(SourceAdapter):
    def download(self) -> DownloadResult:
        seed = Path(__file__).resolve().parents[2] / "data" / "historical_cases" / "seed_cases.json"
        if not seed.exists():
            return DownloadResult(success=False, message="Seed historical cases file missing")
        out_dir = self.dated_raw_dir()
        target = out_dir / "seed_cases.json"
        target.write_bytes(seed.read_bytes())
        return DownloadResult(success=True, message="Copied seed historical cases", files=[target])

    def ingest_manual_files(self, directory: Path) -> ParseResult:
        files = list(directory.glob("*.json")) + list(directory.glob("*.csv"))
        if not files:
            return ParseResult(success=False, message=f"No historical case files in {directory}")
        return self.parse_and_normalize(files)

    def parse_and_normalize(self, raw_files: list[Path]) -> ParseResult:
        from database.session import SessionLocal

        cases: list[dict] = []
        resources: list[dict] = []
        for path in raw_files:
            if path.suffix.lower() == ".json":
                payload = json.loads(path.read_text(encoding="utf-8"))
                cases.extend(payload.get("cases", []))
                resources.extend(payload.get("resources", []))
            elif path.suffix.lower() == ".csv":
                with path.open(encoding="utf-8-sig", newline="") as f:
                    for row in csv.DictReader(f):
                        cases.append(row)

        db = SessionLocal()
        written = 0
        try:
            for case in cases:
                event_id = case["event_id"]
                existing = db.query(HistoricalCase).filter_by(event_id=event_id).one_or_none()
                fields = {k: case.get(k) for k in HistoricalCase.__table__.columns.keys() if k != "id"}
                if existing:
                    for k, v in fields.items():
                        setattr(existing, k, v)
                else:
                    db.add(HistoricalCase(**fields))
                written += 1
            for res in resources:
                db.add(HistoricalResource(**{k: res.get(k) for k in HistoricalResource.__table__.columns.keys() if k != "id"}))
            db.add(
                DataVersion(
                    source_id=self.source.source_id,
                    version_label=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                    checksum=hashlib.sha256(b"".join(p.read_bytes() for p in raw_files)).hexdigest(),
                    raw_path=str(raw_files[0].parent),
                    download_timestamp=datetime.now(timezone.utc),
                    source_url=self.source.url,
                    parse_status="success",
                )
            )
            db.commit()
        finally:
            db.close()

        return ParseResult(success=True, message=f"Loaded {written} historical cases", records_written=written)
