from typing import Any, Literal

from pydantic import BaseModel, Field


PopulationStatus = Literal["reported", "woa_bp_estimated", "unknown"]


class EventBlock(BaseModel):
    date: str = ""
    time: str = ""
    magnitude: float | None = None
    depth_km: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    location: str = ""
    state: str = ""
    district: str = ""


class PopulationBlock(BaseModel):
    affected_population: int | None = None
    population_source: str = ""
    population_status: PopulationStatus = "unknown"
    population_density: float | None = None
    urban_rural: str = ""
    vulnerable_population: dict[str, Any] = Field(default_factory=dict)


class GeographyBlock(BaseModel):
    terrain: str = ""
    elevation: float | None = None
    seismic_zone: str = ""
    remote: bool = False


class EnvironmentBlock(BaseModel):
    temperature: float | None = None
    rainfall: float | None = None
    season: str = ""


class DamageBlock(BaseModel):
    deaths: int | None = None
    injuries: int | None = None
    buildings_damaged: int | None = None
    buildings_collapsed: int | None = None
    roads_damaged: int | None = None
    bridges_damaged: int | None = None
    hospital_damage: bool | None = None
    power_outage: bool | None = None
    water_disruption: bool | None = None
    communication_disruption: bool | None = None


class EarthquakeScenario(BaseModel):
    event: EventBlock = Field(default_factory=EventBlock)
    population: PopulationBlock = Field(default_factory=PopulationBlock)
    geography: GeographyBlock = Field(default_factory=GeographyBlock)
    environment: EnvironmentBlock = Field(default_factory=EnvironmentBlock)
    damage: DamageBlock = Field(default_factory=DamageBlock)
    response_phase: str = ""
