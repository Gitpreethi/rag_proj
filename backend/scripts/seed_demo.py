"""Seed demo data for Bhuj 2001 end-to-end pipeline (manual authoritative documents expected)."""

import json
import shutil
from pathlib import Path

from config.settings import get_settings
from data_pipeline.sync import sync_source
from database.models import MaterialTaxonomy
from database.session import SessionLocal, init_db
from rag.ingestion.document_pipeline import ingest_registered_documents

ROOT = Path(__file__).resolve().parents[2]
BACKEND = Path(__file__).resolve().parents[1]


def main() -> None:
    settings = get_settings()
    init_db()

    # Historical cases seed
    hist_dir = settings.raw_data_root / "historical_earthquake_reports"
    hist_dir.mkdir(parents=True, exist_ok=True)
    seed = BACKEND / "data" / "historical_cases" / "seed_cases.json"
    shutil.copy(seed, hist_dir / "seed_cases.json")
    sync_source("historical_earthquake_reports", force=True)

    # Sample NCS event (Bhuj aftershock-style record for pipeline testing; replace with official NCS export)
    ncs_dir = settings.raw_data_root / "ncs_earthquake_archive"
    ncs_dir.mkdir(parents=True, exist_ok=True)
    sample_ncs = ncs_dir / "sample_ncs_events.csv"
    if not sample_ncs.exists():
        sample_ncs.write_text(
            "event_id,date,origin_time,latitude,longitude,depth_km,magnitude,magnitude_type,location,state,district\n"
            "ncs_bhuj_2001_main,2001-01-26,08:46:00,23.36,70.34,16.0,7.7,Mw,Bhuj Kachchh Gujarat,Gujarat,Kachchh\n",
            encoding="utf-8",
        )
    sync_source("ncs_earthquake_archive", force=True)

    # Placeholder guideline text until official PDFs are manually added
    nidm_dir = settings.raw_data_root / "nidm_earthquake_guidelines"
    nidm_dir.mkdir(parents=True, exist_ok=True)
    demo_doc = nidm_dir / "earthquake_emergency_management_placeholder.txt"
    if not demo_doc.exists():
        demo_doc.write_text(
            "National Disaster Management Guidelines — Management of Earthquakes (Placeholder)\n\n"
            "Section: Immediate Response (0-72 hours)\n"
            "Focus on search and rescue, medical care, safe shelter, water, and sanitation.\n"
            "Quantitative standards must be taken only from officially ingested tables.\n",
            encoding="utf-8",
        )
    sync_source("nidm_earthquake_guidelines", force=True)

    # Material taxonomy
    taxonomy = json.loads((BACKEND / "data" / "material_taxonomy" / "categories.json").read_text(encoding="utf-8"))
    db = SessionLocal()
    try:
        for row in taxonomy:
            existing = db.query(MaterialTaxonomy).filter_by(material_id=row["material_id"]).one_or_none()
            if existing:
                continue
            db.add(MaterialTaxonomy(**row))
        db.commit()
    finally:
        db.close()

    ingest_registered_documents(reindex=True)
    print("Demo seed complete. Run POST /rag/query with Bhuj or Himalayan scenario.")


if __name__ == "__main__":
    main()
