from sqlalchemy.orm import Session

from database.models import GeologyRecord, HistoricalCase, HistoricalResource, PopulationRecord, ResourceStandard
from database.session import SessionLocal


def fetch_historical_cases(state: str | None = None, limit: int = 5) -> list[dict]:
    db: Session = SessionLocal()
    try:
        q = db.query(HistoricalCase)
        if state:
            q = q.filter(HistoricalCase.state.ilike(f"%{state}%"))
        rows = q.limit(limit).all()
        return [
            {
                "event_id": r.event_id,
                "event_name": r.event_name,
                "date": r.date,
                "magnitude": r.magnitude,
                "state": r.state,
                "district": r.district,
                "terrain": r.terrain,
                "population_affected": r.population_affected,
                "deaths": r.deaths,
                "source_documents": r.source_documents,
            }
            for r in rows
        ]
    finally:
        db.close()


def fetch_historical_resources(event_id: str | None = None, limit: int = 20) -> list[dict]:
    db: Session = SessionLocal()
    try:
        q = db.query(HistoricalResource)
        if event_id:
            q = q.filter_by(event_id=event_id)
        rows = q.limit(limit).all()
        return [
            {
                "event_id": r.event_id,
                "resource_name": r.resource_name,
                "resource_category": r.resource_category,
                "quantity": r.quantity,
                "unit": r.unit,
                "reported_or_estimated": r.reported_or_estimated,
                "source": r.source,
            }
            for r in rows
        ]
    finally:
        db.close()


def fetch_population_context(state: str | None, district: str | None) -> dict | None:
    if not state and not district:
        return None
    db: Session = SessionLocal()
    try:
        q = db.query(PopulationRecord)
        if district:
            q = q.filter(PopulationRecord.district.ilike(f"%{district}%"))
        elif state:
            q = q.filter(PopulationRecord.state.ilike(f"%{state}%"))
        row = q.first()
        if not row:
            return None
        return {
            "state": row.state,
            "district": row.district,
            "population": row.population,
            "population_density": row.population_density,
            "urban_rural": row.urban_rural,
            "source": row.source,
        }
    finally:
        db.close()


def fetch_resource_standards(material_category: str | None = None) -> list[dict]:
    db: Session = SessionLocal()
    try:
        q = db.query(ResourceStandard)
        if material_category:
            q = q.filter(ResourceStandard.category.ilike(f"%{material_category}%"))
        return [
            {
                "name": r.name,
                "category": r.category,
                "per_capita_quantity": r.per_capita_quantity,
                "unit": r.unit,
                "duration_days": r.duration_days,
                "phase": r.phase,
                "authority": r.authority,
                "source": r.source,
            }
            for r in q.all()
        ]
    finally:
        db.close()


def fetch_geology(state: str | None, district: str | None) -> dict | None:
    db: Session = SessionLocal()
    try:
        q = db.query(GeologyRecord)
        if district:
            q = q.filter(GeologyRecord.district.ilike(f"%{district}%"))
        elif state:
            q = q.filter(GeologyRecord.state.ilike(f"%{state}%"))
        row = q.first()
        if not row:
            return None
        return {
            "seismic_zone": row.seismic_zone,
            "fault_info": row.fault_info,
            "tectonic_notes": row.tectonic_notes,
            "source": row.source,
        }
    finally:
        db.close()
