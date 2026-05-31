from typing import Any

import numpy as np
import pandas as pd

from pipeline.raw.cycle_parser import parse_cycle


def normalize_measurement_column(field_name: str) -> str:
    return field_name.strip().lower()


def convert_measurement_value(
    field_name: str,
    value: Any,
) -> dict[str, Any]:
    normalized_name = normalize_measurement_column(field_name)

    if np.iscomplexobj(value):
        return {
            f"{normalized_name}_real": float(np.real(value)),
            f"{normalized_name}_imag": float(np.imag(value)),
        }

    if isinstance(value, np.generic):
        return {normalized_name: value.item()}

    return {normalized_name: value}


def build_measurement_readings_for_battery(
    battery_id: str,
    cycles: list[Any],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for cycle_index, cycle in enumerate(cycles):
        parsed = parse_cycle(
            cycle=cycle,
            battery_id=battery_id,
            cycle_index=cycle_index,
        )

        measurement_arrays = {
            field_name: value
            for field_name, value in parsed["data"].items()
            if isinstance(value, np.ndarray) and len(value) > 0
        }

        if not measurement_arrays:
            continue

        aligned_lengths = {
            len(values)
            for values in measurement_arrays.values()
        }
        sample_count = max(aligned_lengths)

        for sample_index in range(sample_count):
            row: dict[str, Any] = {
                "battery_id": battery_id,
                "cycle_index": cycle_index,
                "operation_type": parsed["operation_type"],
                "start_time": parsed["start_time"],
                "sample_index": sample_index,
            }

            for field_name, values in measurement_arrays.items():
                if len(values) != sample_count:
                    continue

                row.update(
                    convert_measurement_value(
                        field_name=field_name,
                        value=values[sample_index],
                    )
                )

            rows.append(row)

    return pd.DataFrame(rows)
