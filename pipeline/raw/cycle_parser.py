from typing import Any

import numpy as np


def to_1d_array(value: Any) -> np.ndarray:
    if value is None:
        return np.array([])

    array = np.asarray(value)

    if array.ndim == 0:
        return np.array([array.item()])

    return array.flatten()


def get_optional_field(obj: Any, field_name: str, default: Any = None) -> Any:
    if hasattr(obj, field_name):
        return getattr(obj, field_name)

    return default


def matlab_time_vector_to_string(value: Any) -> str | None:
    vector = to_1d_array(value)

    if len(vector) < 5:
        return None

    year = int(vector[0])
    month = int(vector[1])
    day = int(vector[2])
    hour = int(vector[3])
    minute = int(vector[4])
    second = int(vector[5]) if len(vector) > 5 else 0

    return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"


def parse_cycle(cycle: Any, battery_id: str, cycle_index: int) -> dict[str, Any]:
    cycle_type = str(cycle.type)
    data = cycle.data

    parsed = {
        "battery_id": battery_id,
        "cycle_index": cycle_index,
        "operation_type": cycle_type,
        "start_time": matlab_time_vector_to_string(get_optional_field(cycle, "time")),
        "ambient_temperature": get_optional_field(cycle, "ambient_temperature"),
        "data": {},
    }

    data_fields = [
        field
        for field in dir(data)
        if not field.startswith("_")
    ]

    for field in data_fields:
        value = getattr(data, field)

        if isinstance(value, np.ndarray):
            parsed["data"][field] = to_1d_array(value)
        else:
            parsed["data"][field] = value

    return parsed