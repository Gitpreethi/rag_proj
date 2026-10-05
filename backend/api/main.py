from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from data_pipeline.sync import sync_all, sync_source
from database.session import get_db, init_db
from rag.generation.pipeline import run_rag_query
from rag.ingestion.document_pipeline import ingest_registered_documents
from rag.schemas.earthquake_scenario import EarthquakeScenario
from sources.registry import SourceRegistry

app = FastAPI(
    title="India Post-Earthquake Emergency Intelligence API",
    version="0.1.0",
    description="Evidence-grounded RAG system for earthquake material/resource demand prediction (India-specific).",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


class QueryRequest(BaseModel):
    question: str
    scenario: dict | None = None


class IngestRequest(BaseModel):
    source_id: str | None = None
    reindex: bool = False


@app.get("/rag/health")
def rag_health(db: Session = Depends(get_db)):
    registry = SourceRegistry()
    return {
        "status": "ok",
        "sources_registered": len(registry.list_sources(enabled_only=False)),
        "database": "connected",
    }


@app.get("/rag/sources")
def rag_sources():
    registry = SourceRegistry()
    return [registry.to_public_dict(s) for s in registry.list_sources(enabled_only=False)]


@app.get("/data/status")
def data_status(db: Session = Depends(get_db)):
    from database.models import DataVersion, DocumentRegistry, EarthquakeEvent, HistoricalCase

    latest = db.query(DataVersion).order_by(DataVersion.id.desc()).limit(10).all()
    return {
        "earthquake_events": db.query(EarthquakeEvent).count(),
        "historical_cases": db.query(HistoricalCase).count(),
        "documents_registered": db.query(DocumentRegistry).count(),
        "recent_versions": [
            {
                "source_id": v.source_id,
                "version_label": v.version_label,
                "checksum": v.checksum,
                "parse_status": v.parse_status,
            }
            for v in latest
        ],
    }


@app.post("/data/sync")
def data_sync_all(force: bool = False):
    reports = sync_all(force=force)
    return [
        {
            "source_id": r.source_id,
            "download": r.download,
            "parse": r.parse,
            "records_written": r.records_written,
            "skipped": r.skipped,
            "errors": r.errors,
        }
        for r in reports
    ]


@app.post("/data/sync/{source_id}")
def data_sync_one(source_id: str, force: bool = False):
    try:
        report = sync_source(source_id, force=force)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "source_id": report.source_id,
        "download": report.download,
        "parse": report.parse,
        "records_written": report.records_written,
        "skipped": report.skipped,
        "errors": report.errors,
    }


@app.post("/rag/ingest")
def rag_ingest(body: IngestRequest):
    result = ingest_registered_documents(source_id=body.source_id, reindex=body.reindex)
    return result


@app.post("/rag/reindex")
def rag_reindex(body: IngestRequest = IngestRequest()):
    return ingest_registered_documents(source_id=body.source_id, reindex=True)


@app.post("/rag/query")
def rag_query(body: QueryRequest):
    return run_rag_query(body.question, body.scenario)


@app.get("/scenario/template")
def scenario_template():
    return EarthquakeScenario().model_dump()
