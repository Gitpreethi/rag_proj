def calculate_total_demand(
    affected_population: int | None,
    per_capita_quantity: float | None,
    duration_days: float | None,
) -> dict | None:
    if affected_population is None or per_capita_quantity is None:
        return None
    total = affected_population * per_capita_quantity
    calc = f"{affected_population} × {per_capita_quantity}"
    if duration_days is not None:
        total *= duration_days
        calc += f" × {duration_days}"
    return {
        "affected_population": affected_population,
        "per_capita_quantity": per_capita_quantity,
        "duration_days": duration_days,
        "total_quantity": total,
        "calculation": calc,
        "basis": "calculated",
    }
