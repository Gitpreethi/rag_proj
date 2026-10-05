from datetime import datetime, timezone

from config.settings import get_settings
from population_model.woa_bp.predictor import PopulationPredictor
from rag.generation.demand_calculation import calculate_total_demand
from rag.generation.llm_client import ReasoningLLM
from rag.query_expansion.expander import expand_query_for_retrieval
from rag.query_understanding.parser import build_structured_query
from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.structured import (
    fetch_geology,
    fetch_historical_cases,
    fetch_historical_resources,
    fetch_population_context,
    fetch_resource_standards,
)
from rag.schemas.earthquake_scenario import EarthquakeScenario
from rag.schemas.structured_output import StructuredPrediction


def run_rag_query(question: str, scenario: dict | None = None) -> dict:
    settings = get_settings()
    eq = EarthquakeScenario.model_validate(scenario or {})
    structured_query = build_structured_query(question, eq)
    retrieval_query = expand_query_for_retrieval(structured_query)

    filters = {}
    if structured_query.get("state"):
        filters["state"] = structured_query["state"]

    retriever = HybridRetriever()
    evidence = retriever.retrieve(retrieval_query, filters=filters or None)

    pop_predictor = PopulationPredictor()
    population_block = eq.population
    if population_block.population_status == "unknown" and population_block.affected_population is None:
        estimate = pop_predictor.predict(eq)
        if estimate.get("status") == "woa_bp_estimated":
            population_block.population_status = "woa_bp_estimated"
            population_block.affected_population = estimate.get("value")
            population_block.population_source = estimate.get("source", "WOA-BP")

    structured = StructuredPrediction(
        earthquake_summary={
            "magnitude": eq.event.magnitude,
            "depth_km": eq.event.depth_km,
            "location": eq.event.location,
            "date": eq.event.date,
            "terrain": eq.geography.terrain,
            "season": eq.environment.season,
        },
        affected_population={
            "value": population_block.affected_population,
            "source": population_block.population_source,
            "status": population_block.population_status,
        },
        response_phase=eq.response_phase or structured_query.get("response_phase", ""),
        historical_cases=fetch_historical_cases(state=eq.event.state),
        population_prediction={
            "model": population_block.population_status,
            "value": population_block.affected_population,
            "uncertainty": pop_predictor.last_uncertainty,
            "source": population_block.population_source,
        },
    )

    calculations = []
    for std in fetch_resource_standards():
        calc = calculate_total_demand(
            population_block.affected_population,
            std.get("per_capita_quantity"),
            std.get("duration_days"),
        )
        if calc:
            calc["material"] = std.get("name")
            calc["source"] = std.get("source")
            calculations.append(calc)
            structured.emergency_materials.append(
                {
                    "category": std.get("category"),
                    "material": std.get("name"),
                    "per_capita_quantity": std.get("per_capita_quantity"),
                    "unit": std.get("unit"),
                    "duration": std.get("duration_days"),
                    "total_quantity": calc["total_quantity"],
                    "basis": "calculated",
                    "source": std.get("source"),
                    "confidence": None,
                }
            )

    structured.calculations = calculations
    structured.citations = [
        {
            "chunk_id": ev.get("chunk_id"),
            "authority": ev.get("metadata", {}).get("authority"),
            "document_id": ev.get("metadata", {}).get("document_id"),
            "section": ev.get("metadata", {}).get("section"),
            "url": ev.get("metadata", {}).get("url"),
            "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        for ev in evidence
    ]

    if not structured.emergency_materials:
        structured.uncertainties.append(
            "No authoritative per-capita material standards loaded in resource_standards table."
        )

    llm_input = {
        "structured_query": structured_query,
        "scenario": eq.model_dump(),
        "structured_data": {
            "population_context": fetch_population_context(eq.event.state, eq.event.district),
            "geology": fetch_geology(eq.event.state, eq.event.district),
            "historical_resources": fetch_historical_resources(),
        },
        "evidence": evidence,
        "historical_cases": structured.historical_cases,
        "reproducibility": {
            "embedding_model": settings.embedding_model,
            "reranker_model": settings.reranker_model,
            "llm_model": settings.llm_model,
            "prompt_version": settings.prompt_version,
            "hybrid_alpha": settings.hybrid_alpha,
            "random_seed": settings.random_seed,
        },
    }

    answer = ReasoningLLM().generate(llm_input)
    return {
        "answer": answer,
        "structured_prediction": structured.model_dump(),
        "evidence": evidence,
        "sources": structured.citations,
        "calculations": calculations,
        "uncertainties": structured.uncertainties,
    }
