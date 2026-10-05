from typing import Any


def validate_earthquake_row(row: dict[str, Any]) -> tuple[bool, str]:
    if not row.get("event_id"):
        return False, "Missing event_id"
    lat = row.get("latitude")
    lon = row.get("longitude")
    if lat is not None and not (-90 <= float(lat) <= 90):
        return False, f"Invalid latitude: {lat}"
    if lon is not None and not (-180 <= float(lon) <= 180):
        return False, f"Invalid longitude: {lon}"
    mag = row.get("magnitude")
    if mag is not None and not (0 <= float(mag) <= 10.5):
        return False, f"Suspicious magnitude: {mag}"
    depth = row.get("depth_km")
    if depth is not None and float(depth) < 0:
        return False, f"Invalid depth: {depth}"
    return True, ""
