from typing import Any, Literal

from pydantic import BaseModel, Field

BasisType = Literal[
    "official_standard",
    "historical_case",
    "calculated",
    "woa_bp_related",
    "inference",
    "unknown",
]


class StructuredPrediction(BaseModel):
    earthquake_summary: dict[str, Any] = Field(default_factory=dict)
    affected_population: dict[str, Any] = Field(default_factory=dict)
    response_phase: str = ""
    context_factors: list[dict[str, Any]] = Field(default_factory=list)
    historical_cases: list[dict[str, Any]] = Field(default_factory=list)
    emergency_materials: list[dict[str, Any]] = Field(default_factory=list)
    response_resources: list[dict[str, Any]] = Field(default_factory=list)
    population_prediction: dict[str, Any] = Field(default_factory=dict)
    priority_factors: list[str] = Field(default_factory=list)
    calculations: list[dict[str, Any]] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    citations: list[dict[str, Any]] = Field(default_factory=list)
