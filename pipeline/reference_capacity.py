DEFAULT_REFERENCE_CAPACITY_AH = 2.0

# NASA battery IDs are stored as four digits in the MAT filenames.
BATTERY_REFERENCE_CAPACITY_AH: dict[str, float] = {}


def normalize_battery_id(battery_id: str) -> str:
    normalized = battery_id.strip().upper()

    if normalized.startswith("B") and normalized[1:].isdigit():
        return f"B{int(normalized[1:]):04d}"

    return normalized


def get_reference_capacity_ah(battery_id: str) -> float:
    normalized = normalize_battery_id(battery_id)

    return BATTERY_REFERENCE_CAPACITY_AH.get(
        normalized,
        DEFAULT_REFERENCE_CAPACITY_AH,
    )
