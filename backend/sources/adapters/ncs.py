import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from config.settings import get_settings
from database.models import DataVersion, EarthquakeEvent
from data_pipeline.validation import validate_earthquake_row
from sources.adapters.base import DownloadResult, ParseResult, SourceAdapter


class NCSAdapter(SourceAdapter):
    def download(self) -> DownloadResult:
        settings = get_settings()
        url = settings.ncs_events_url.strip()
        if not url:
            return DownloadResult(
                success=False,
                skipped=True,
                message=(
                    "NCS automatic download not configured. Set NCS_EVENTS_URL or place "
                    "CSV/JSON under data/raw/ncs_earthquake_archive/ (manual snapshot)."
                ),
            )
        if settings.ncs_api_key:
            headers = {"Authorization": f"Bearer {settings.ncs_api_key}"}
        else:
            headers = {}

        out_dir = self.dated_raw_dir()
        try:
            with httpx.Client(timeout=60.0, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                ext = "json" if "json" in response.headers.get("content-type", "") else "dat"
                out_path = out_dir / f"ncs_events.{ext}"
                out_path.write_bytes(response.content)
        except httpx.HTTPError as exc:
            return DownloadResult(success=False, message=f"NCS download failed: {exc}")

        checksum = hashlib.sha256(out_path.read_bytes()).hexdigest()
        meta = {
            "source_url": url,
            "download_timestamp": datetime.now(timezone.utc).isoformat(),
            "checksum": checksum,
            "authority": self.source.authority,
        }
        (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return DownloadResult(success=True, message="NCS file downloaded", files=[out_path], metadata=meta)

    def ingest_manual_files(self, directory: Path) -> ParseResult:
        files = []
        for pattern in ("*.csv", "*.json"):
            files.extend(directory.glob(pattern))
        if not files:
            return ParseResult(success=False, message=f"No CSV/JSON found in {directory}")
        return self.parse_and_normalize(files)

    def parse_and_normalize(self, raw_files: list[Path]) -> ParseResult:
        from database.session import SessionLocal

        records: list[dict] = []
        errors: list[str] = []
        for path in raw_files:
            if path.suffix.lower() == ".csv":
                with path.open(encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(self._normalize_row(row, path))
            elif path.suffix.lower() == ".json":
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for row in data:
                        records.append(self._normalize_row(row, path))
                elif isinstance(data, dict) and "events" in data:
                    for row in data["events"]:
                        records.append(self._normalize_row(row, path))

        written = 0
        db: Session = SessionLocal()
        try:
            for row in records:
                ok, err = validate_earthquake_row(row)
                if not ok:
                    errors.append(err)
                    continue
                event_id = row["event_id"]
                existing = db.query(EarthquakeEvent).filter_by(event_id=event_id).one_or_none()
                if existing:
                    for key, value in row.items():
                        setattr(existing, key, value)
                else:
                    db.add(EarthquakeEvent(**row))
                written += 1
            checksum = hashlib.sha256(b"".join(p.read_bytes() for p in raw_files)).hexdigest()
            db.add(
                DataVersion(
                    source_id=self.source.source_id,
                    version_label=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                    checksum=checksum,
                    raw_path=str(raw_files[0].parent),
                    download_timestamp=datetime.now(timezone.utc),
                    source_url=self.source.url,
                    license_notes=self.source.license_notes,
                    parse_status="success" if not errors else "partial",
                    notes="; ".join(errors[:20]),
                )
            )
            db.commit()
        finally:
            db.close()

        return ParseResult(
            success=written > 0,
            message=f"NCS parse complete: {written} events",
            records_written=written,
            errors=errors,
        )

    def _normalize_row(self, row: dict, path: Path) -> dict:
        def pick(*keys: str):
            for k in keys:
                if k in row and row[k] not in (None, ""):
                    return row[k]
            return None

        event_id = pick("event_id", "id", "EventID")
        if not event_id:
            lat = pick("latitude", "lat", "Latitude")
            lon = pick("longitude", "lon", "Longitude")
            date = pick("date", "Date", "origin_date")
            event_id = f"ncs_{date}_{lat}_{lon}".replace(" ", "_")

        return {
            "event_id": str(event_id),
            "date": pick("date", "Date", "origin_date"),
            "origin_time": pick("origin_time", "time", "Time", "OriginTime"),
            "latitude": float(pick("latitude", "lat", "Latitude")) if pick("latitude", "lat") else None,
            "longitude": float(pick("longitude", "lon", "Longitude")) if pick("longitude", "lon") else None,
            "depth_km": float(pick("depth_km", "depth", "Depth")) if pick("depth_km", "depth", "Depth") else None,
            "magnitude": float(pick("magnitude", "mag", "Magnitude")) if pick("magnitude", "mag") else None,
            "magnitude_type": pick("magnitude_type", "mag_type", "MagnitudeType"),
            "location": pick("location", "place", "Location"),
            "region": pick("region", "Region"),
            "state": pick("state", "State"),
            "district": pick("district", "District"),
            "source_url": self.source.url,
            "source_authority": self.source.authority,
            "dataset_version": path.parent.name,
            "license_notes": self.source.license_notes,
            "raw_checksum": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
