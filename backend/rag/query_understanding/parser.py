import re
from typing import Any

from rag.schemas.earthquake_scenario import EarthquakeScenario


QUESTION_TYPES = {
    "material_demand",
    "historical_case",
    "guideline",
    "resource_requirement",
    "population",
    "damage",
    "multi_document_reasoning",
}


def infer_question_type(question: str) -> str:
    q = question.lower()
    if "historical" in q or "similar" in q or "comparable" in q:
        return "historical_case"
    if "guideline" in q or "ndma" in q or "nidm" in q:
        return "guideline"
    if "resource" in q or "ndrf" in q or "team" in q:
        return "resource_requirement"
    if "population" in q or "affected" in q:
        return "population"
    if "damage" in q or "casualt" in q:
        return "damage"
    if "material" in q or "supply" in q or "relief" in q:
        return "material_demand"
    return "multi_document_reasoning"


def extract_magnitude(text: str) -> float | None:
    m = re.search(r"\bM?\s?(\d\.\d)\s*(?:magnitude|richter)?\b", text, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"\b(\d\.\d)\s*magnitude\b", text, re.I)
    return float(m.group(1)) if m else None


def extract_affected_population(text: str) -> int | None:
    m = re.search(r"(\d[\d,]*)\s+people\s+(?:are\s+)?affected", text, re.I)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def infer_season(text: str) -> str:
    months = {
        "january": "winter",
        "february": "winter",
        "december": "winter",
        "june": "monsoon",
        "july": "monsoon",
        "august": "monsoon",
        "september": "monsoon",
    }
    lower = text.lower()
    for month, season in months.items():
        if month in lower:
            return season
    if "winter" in lower or "cold" in lower:
        return "winter"
    if "rain" in lower or "monsoon" in lower:
        return "monsoon"
    return ""


def infer_terrain(text: str) -> str:
    lower = text.lower()
    if "mountain" in lower or "himalaya" in lower or "hill" in lower:
        return "mountainous"
    if "urban" in lower or "city" in lower:
        return "urban"
    if "rural" in lower:
        return "rural"
    return ""


def infer_response_phase(text: str) -> str:
    lower = text.lower()
    if "72 hour" in lower or "first 72" in lower or "0-72" in lower:
        return "0_72_hours"
    if "240" in lower or "10 day" in lower:
        return "240_plus_hours"
    if "72-240" in lower or "continued relief" in lower:
        return "72_240_hours"
    return "0_72_hours"


def build_structured_query(question: str, scenario: EarthquakeScenario | None) -> dict[str, Any]:
    scenario = scenario or EarthquakeScenario()
    if scenario.event.magnitude is None:
        scenario.event.magnitude = extract_magnitude(question)
    if scenario.population.affected_population is None:
        ap = extract_affected_population(question)
        if ap is not None:
            scenario.population.affected_population = ap
            scenario.population.population_status = "reported"
            scenario.population.population_source = "user_question"
    if not scenario.environment.season:
        scenario.environment.season = infer_season(question)
    if not scenario.geography.terrain:
        scenario.geography.terrain = infer_terrain(question)
    if not scenario.response_phase:
        scenario.response_phase = infer_response_phase(question)

    return {
        "question": question,
        "question_type": infer_question_type(question),
        "scenario": scenario.model_dump(),
        "magnitude": scenario.event.magnitude,
        "depth_km": scenario.event.depth_km,
        "latitude": scenario.event.latitude,
        "longitude": scenario.event.longitude,
        "location": scenario.event.location,
        "state": scenario.event.state,
        "district": scenario.event.district,
        "season": scenario.environment.season,
        "terrain": scenario.geography.terrain,
        "affected_population": scenario.population.affected_population,
        "population_status": scenario.population.population_status,
        "response_phase": scenario.response_phase,
    }
