from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EarthquakeEvent(Base):
    __tablename__ = "earthquake_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    date: Mapped[str | None] = mapped_column(String(32))
    origin_time: Mapped[str | None] = mapped_column(String(32))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    depth_km: Mapped[float | None] = mapped_column(Float)
    magnitude: Mapped[float | None] = mapped_column(Float)
    magnitude_type: Mapped[str | None] = mapped_column(String(16))
    location: Mapped[str | None] = mapped_column(String(512))
    region: Mapped[str | None] = mapped_column(String(256))
    state: Mapped[str | None] = mapped_column(String(128))
    district: Mapped[str | None] = mapped_column(String(128))
    source_url: Mapped[str | None] = mapped_column(Text)
    source_authority: Mapped[str | None] = mapped_column(String(64))
    dataset_version: Mapped[str | None] = mapped_column(String(64))
    license_notes: Mapped[str | None] = mapped_column(Text)
    raw_checksum: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HistoricalCase(Base):
    __tablename__ = "historical_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    event_name: Mapped[str] = mapped_column(String(256))
    date: Mapped[str | None] = mapped_column(String(32))
    magnitude: Mapped[float | None] = mapped_column(Float)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    depth_km: Mapped[float | None] = mapped_column(Float)
    state: Mapped[str | None] = mapped_column(String(128))
    district: Mapped[str | None] = mapped_column(String(128))
    terrain: Mapped[str | None] = mapped_column(String(128))
    season: Mapped[str | None] = mapped_column(String(64))
    population_affected: Mapped[int | None] = mapped_column(Integer)
    deaths: Mapped[int | None] = mapped_column(Integer)
    injuries: Mapped[int | None] = mapped_column(Integer)
    buildings_damaged: Mapped[int | None] = mapped_column(Integer)
    buildings_collapsed: Mapped[int | None] = mapped_column(Integer)
    roads_damaged: Mapped[int | None] = mapped_column(Integer)
    bridges_damaged: Mapped[int | None] = mapped_column(Integer)
    hospitals_damaged: Mapped[int | None] = mapped_column(Integer)
    power_disruption: Mapped[bool | None] = mapped_column(Boolean)
    water_disruption: Mapped[bool | None] = mapped_column(Boolean)
    communication_disruption: Mapped[bool | None] = mapped_column(Boolean)
    relief_materials: Mapped[dict | None] = mapped_column(JSON)
    rescue_resources: Mapped[dict | None] = mapped_column(JSON)
    medical_resources: Mapped[dict | None] = mapped_column(JSON)
    shelter_resources: Mapped[dict | None] = mapped_column(JSON)
    source_documents: Mapped[dict | None] = mapped_column(JSON)
    notes: Mapped[str | None] = mapped_column(Text)


class HistoricalResource(Base):
    __tablename__ = "historical_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(128), index=True)
    event_name: Mapped[str | None] = mapped_column(String(256))
    resource_category: Mapped[str | None] = mapped_column(String(128))
    resource_name: Mapped[str] = mapped_column(String(256))
    quantity: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str | None] = mapped_column(Text)
    source_date: Mapped[str | None] = mapped_column(String(32))
    reported_or_estimated: Mapped[str | None] = mapped_column(String(32))
    notes: Mapped[str | None] = mapped_column(Text)


class PopulationRecord(Base):
    __tablename__ = "population"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state: Mapped[str | None] = mapped_column(String(128), index=True)
    district: Mapped[str | None] = mapped_column(String(128), index=True)
    sub_district: Mapped[str | None] = mapped_column(String(128))
    town_village: Mapped[str | None] = mapped_column(String(256))
    population: Mapped[int | None] = mapped_column(Integer)
    households: Mapped[int | None] = mapped_column(Integer)
    population_density: Mapped[float | None] = mapped_column(Float)
    urban_rural: Mapped[str | None] = mapped_column(String(32))
    male_population: Mapped[int | None] = mapped_column(Integer)
    female_population: Mapped[int | None] = mapped_column(Integer)
    vulnerable_indicators: Mapped[dict | None] = mapped_column(JSON)
    census_year: Mapped[str | None] = mapped_column(String(16))
    source: Mapped[str | None] = mapped_column(Text)


class CasualtyRecord(Base):
    __tablename__ = "casualties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str | None] = mapped_column(String(128), index=True)
    state_ut: Mapped[str | None] = mapped_column(String(128))
    disaster_category: Mapped[str | None] = mapped_column(String(128))
    deaths: Mapped[int | None] = mapped_column(Integer)
    injuries: Mapped[int | None] = mapped_column(Integer)
    age_sex_breakdown: Mapped[dict | None] = mapped_column(JSON)
    source: Mapped[str | None] = mapped_column(Text)
    source_definition: Mapped[str | None] = mapped_column(Text)


class InfrastructureDamage(Base):
    __tablename__ = "infrastructure_damage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(128), index=True)
    damage_type: Mapped[str] = mapped_column(String(128))
    quantity: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(64))
    reported_or_estimated: Mapped[str | None] = mapped_column(String(32))
    source: Mapped[str | None] = mapped_column(Text)


class WeatherRecord(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state: Mapped[str | None] = mapped_column(String(128))
    district: Mapped[str | None] = mapped_column(String(128))
    date: Mapped[str | None] = mapped_column(String(32))
    temperature_c: Mapped[float | None] = mapped_column(Float)
    rainfall_mm: Mapped[float | None] = mapped_column(Float)
    season: Mapped[str | None] = mapped_column(String(64))
    source: Mapped[str | None] = mapped_column(Text)


class TerrainRecord(Base):
    __tablename__ = "terrain"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state: Mapped[str | None] = mapped_column(String(128))
    district: Mapped[str | None] = mapped_column(String(128))
    terrain_type: Mapped[str | None] = mapped_column(String(128))
    elevation_m: Mapped[float | None] = mapped_column(Float)
    remote: Mapped[bool | None] = mapped_column(Boolean)
    source: Mapped[str | None] = mapped_column(Text)


class GeologyRecord(Base):
    __tablename__ = "geology"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state: Mapped[str | None] = mapped_column(String(128))
    district: Mapped[str | None] = mapped_column(String(128))
    seismic_zone: Mapped[str | None] = mapped_column(String(32))
    fault_info: Mapped[str | None] = mapped_column(Text)
    tectonic_notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(Text)


class ResourceStandard(Base):
    __tablename__ = "resource_standards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_id: Mapped[str | None] = mapped_column(String(64), index=True)
    category: Mapped[str | None] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(256))
    per_capita_quantity: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(64))
    duration_days: Mapped[float | None] = mapped_column(Float)
    phase: Mapped[str | None] = mapped_column(String(32))
    authority: Mapped[str | None] = mapped_column(String(128))
    source: Mapped[str | None] = mapped_column(Text)
    validity: Mapped[str | None] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text)


class MaterialTaxonomy(Base):
    __tablename__ = "material_taxonomy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_id: Mapped[str] = mapped_column(String(64), unique=True)
    category: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(256))
    unit: Mapped[str | None] = mapped_column(String(64))
    per_capita_basis: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(Text)
    authority: Mapped[str | None] = mapped_column(String(128))
    validity: Mapped[str | None] = mapped_column(String(128))
    phase: Mapped[str | None] = mapped_column(String(32))
    notes: Mapped[str | None] = mapped_column(Text)


class SourceRegistryRow(Base):
    __tablename__ = "source_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(512))
    authority: Mapped[str | None] = mapped_column(String(128))
    source_type: Mapped[str | None] = mapped_column(String(64))
    url: Mapped[str | None] = mapped_column(Text)
    download_method: Mapped[str | None] = mapped_column(String(32))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config_json: Mapped[dict | None] = mapped_column(JSON)


class DocumentRegistry(Base):
    __tablename__ = "document_registry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    source_id: Mapped[str] = mapped_column(String(128), index=True)
    title: Mapped[str | None] = mapped_column(String(512))
    authority: Mapped[str | None] = mapped_column(String(128))
    publication_year: Mapped[str | None] = mapped_column(String(16))
    url: Mapped[str | None] = mapped_column(Text)
    local_path: Mapped[str | None] = mapped_column(Text)
    checksum: Mapped[str | None] = mapped_column(String(64))
    jurisdiction: Mapped[str | None] = mapped_column(String(128))
    source_type: Mapped[str | None] = mapped_column(String(64))
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime)


class DataVersion(Base):
    __tablename__ = "data_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(128), index=True)
    version_label: Mapped[str] = mapped_column(String(128))
    checksum: Mapped[str | None] = mapped_column(String(64))
    raw_path: Mapped[str | None] = mapped_column(Text)
    download_timestamp: Mapped[datetime | None] = mapped_column(DateTime)
    source_url: Mapped[str | None] = mapped_column(Text)
    license_notes: Mapped[str | None] = mapped_column(Text)
    parse_status: Mapped[str | None] = mapped_column(String(32))
    notes: Mapped[str | None] = mapped_column(Text)
