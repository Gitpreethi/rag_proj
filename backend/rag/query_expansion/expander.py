def expand_query_for_retrieval(structured_query: dict) -> str:
    """Retrieval-only expansion; not treated as evidence."""
    parts = [structured_query.get("question", "")]
    scenario = structured_query.get("scenario", {})
    event = scenario.get("event", {})
    geo = scenario.get("geography", {})
    env = scenario.get("environment", {})

    if event.get("magnitude"):
        parts.append(f"magnitude {event['magnitude']} earthquake India")
    if event.get("state"):
        parts.append(f"{event['state']} earthquake emergency guidelines")
    if geo.get("terrain") == "mountainous":
        parts.extend(["Himalayan earthquake response", "mountainous terrain logistics"])
    if env.get("season") == "winter":
        parts.extend(["cold weather emergency shelter", "blankets winter clothing heating"])
    if structured_query.get("response_phase") == "0_72_hours":
        parts.append("immediate emergency response 0-72 hours relief materials")
    parts.append("NIDM NDMA earthquake management India")
    return " ".join(p for p in parts if p)
