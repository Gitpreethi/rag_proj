from rag.query_understanding.parser import build_structured_query
from rag.schemas.earthquake_scenario import EarthquakeScenario


def test_extracts_magnitude_and_population():
    q = (
        "M6.5 earthquake occurred in a mountainous district in January. "
        "50,000 people are affected. What materials for first 72 hours?"
    )
    structured = build_structured_query(q, EarthquakeScenario())
    assert structured["magnitude"] == 6.5
    assert structured["affected_population"] == 50000
    assert structured["population_status"] == "reported"
    assert structured["response_phase"] == "0_72_hours"
